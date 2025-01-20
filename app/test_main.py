import contextlib
from datetime import datetime, timedelta

from creyPY.fastapi.db.session import SQLALCHEMY_DATABASE_URL, get_db
from creyPY.fastapi.models.base import Base
from creyPY.fastapi.testing import GenericClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

from app.models.entry import LogEntry
from app.services.auth import verify
from app.setup import delete_old_logs

from .main import app

CURRENT_USER = "api-key|testing"
ENTRY_EXAMPLES = [
    {
        "l_type": "info",
        "t_type": "create",
        "message": "User Max Mustermann created",
        "environment": "dev",
    },
    {
        "l_type": "info",
        "t_type": "update",
        "message": "User Max Mustermann updated",
        "environment": "dev",
    },
    {
        "l_type": "info",
        "t_type": "create",
        "author": "auth|max_muster",
        "message": "User Max Mustermann created a Unit",
        "object_reference": "1",
        "environment": "dev",
    },
    {
        "l_type": "info",
        "t_type": "update",
        "author": "auth|max_muster",
        "message": "User Max Mustermann updated Unit 1",
        "object_reference": "1",
        "previous_object": {"name": "Unit 1"},
        "environment": "prod",
    },
    {
        "l_type": "warning",
        "t_type": "delete",
        "message": "User Max Mustermann deleted",
        "environment": "prod",
    },
]


@contextlib.contextmanager
def app_context(self, name: str = "Testing", retention_days: int | None = None):
    app_id = self.create_app(name, retention_days)
    try:
        yield app_id
    finally:
        self.destroy_app(app_id)


@contextlib.contextmanager
def log_examples(self):
    with app_context(self) as app_id:
        for entry in ENTRY_EXAMPLES:
            self.log_message({"application": app_id, **entry})
        yield app_id


class TestAPI:
    def setup_class(self):
        self.engine = create_engine(SQLALCHEMY_DATABASE_URL + "test", pool_pre_ping=True)
        if database_exists(self.engine.url):
            drop_database(self.engine.url)
        create_database(self.engine.url)

        Base.metadata.create_all(self.engine)

        def get_db_test():
            db = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)()
            try:
                yield db
            finally:
                db.close()

        def get_test_sub():
            global CURRENT_USER
            return CURRENT_USER

        self.db_instance = get_db_test()
        app.dependency_overrides[get_db] = get_db_test
        app.dependency_overrides[verify] = get_test_sub
        self.c = GenericClient(app)

    def teardown_class(self):
        drop_database(self.engine.url)

    # HELPERS
    def create_app(self, name: str = "Testing", retention_days: int | None = None):
        re = self.c.post("/app/", {"name": name, "retention_days": retention_days})
        return re["id"]

    def destroy_app(self, app_id):
        self.c.delete(f"/app/{app_id}")

    def log_message(self, entry_obj):
        re = self.c.post("/log/", entry_obj)
        return re["id"]

    # GENERIC TEST CASES
    def test_swagger_gen(self):
        re = self.c.get("/openapi.json")
        assert re["info"]["title"] == "ApiLog API"

    def test_health_check(self):
        self.c.get("/", parse_json=False)

    # TESTS for module application
    def test_application_api(self):
        self.c.obj_lifecycle({"name": "Testing"}, "/app/")

    def test_application_search(self):
        with app_context(self, "testing 1") as app_id1:
            with app_context(self, "second app 2") as app_id2:
                re = self.c.get("/app/")
                assert re["total"] == 2
                assert len(re["results"]) == 2

                re = self.c.get("/app/?search=testing")
                assert re["total"] == 1
                assert len(re["results"]) == 1

                re = self.c.get("/app/?search=2")
                assert re["total"] == 1
                assert len(re["results"]) == 1

    # TESTS for module log
    def test_log_api(self):
        with app_context(self) as app_id:
            self.c.obj_lifecycle({"application": app_id}, "/log/")

    def test_logging_standards(self):
        with app_context(self) as app_id:
            re = self.c.post("/log/", {"application": app_id})
            log_id = re["id"]
            assert re["application"] == app_id
            assert re["l_type"] == "info"
            assert re["t_type"] == "undefined"
            assert re["message"] == None
            assert re["author"] == "system"
            assert re["environment"] == "prod"
            assert re["object_reference"] == None
            assert re["previous_object"] == None
            assert re["created_by_id"] == CURRENT_USER

            self.c.delete(f"/log/{log_id}")

    def test_logging_search(self):
        with log_examples(self) as app_id:
            re = self.c.get("/log/")
            assert re["total"] == 5
            assert len(re["results"]) == 5

            re = self.c.get("/log/?search=auth|max_muster")
            assert re["total"] == 2
            assert len(re["results"]) == 2

            re = self.c.get("/log/?search=system")
            assert re["total"] == 3
            assert len(re["results"]) == 3

            re = self.c.get("/log/?search=created%20a%20Unit")
            assert re["total"] == 1
            assert len(re["results"]) == 1

    def test_logging_order(self):
        with log_examples(self) as app_id:
            re = self.c.get("/log/?order_by=created_at")
            assert re["total"] == 5
            assert len(re["results"]) == 5
            assert re["results"][0]["created_at"] < re["results"][1]["created_at"]

            re = self.c.get("/log/?order_by=-created_at")
            assert re["total"] == 5
            assert len(re["results"]) == 5
            assert re["results"][0]["created_at"] > re["results"][1]["created_at"]

    def test_logging_filter(self):
        with log_examples(self) as app_id:
            # API KEY
            re = self.c.get("/log/?created_by_id=" + CURRENT_USER)
            assert re["total"] == 5
            assert len(re["results"]) == 5

            # LogType
            re = self.c.get("/log/?l_type=info")
            assert re["total"] == 4
            assert len(re["results"]) == 4

            # TransactionType
            re = self.c.get("/log/?t_type=create")
            assert re["total"] == 2
            assert len(re["results"]) == 2

            # TransactipnType create and update
            re = self.c.get("/log/?t_type%5Bin%5D=create,update")
            assert re["total"] == 4
            assert len(re["results"]) == 4

            # Application
            re = self.c.get("/log/?application=" + app_id)
            assert re["total"] == 5
            assert len(re["results"]) == 5

            # Application not
            re = self.c.get("/log/?application%5Bne%5D=" + app_id)
            assert re["total"] == 0
            assert len(re["results"]) == 0

            # Object Reference
            re = self.c.get("/log/?object_reference=1")
            assert re["total"] == 2
            assert len(re["results"]) == 2

            # author
            re = self.c.get("/log/?author=auth|max_muster")
            assert re["total"] == 2
            assert len(re["results"]) == 2

            # not author
            re = self.c.get("/log/?author%5Bne%5D=auth|max_muster")
            assert re["total"] == 3
            assert len(re["results"]) == 3

            # environment
            re = self.c.get("/log/?environment=dev")
            assert re["total"] == 3
            assert len(re["results"]) == 3

            # application and environment
            re = self.c.get("/log/?application=" + app_id + "&environment=prod")
            assert re["total"] == 2
            assert len(re["results"]) == 2

    def test_logging_delete(self):
        with log_examples(self) as app_id:
            re = self.c.delete("/log/?application=" + str(app_id) + "&environment=prod", r_code=200)
            assert re == 2

            re = self.c.get("/log/?application=" + str(app_id) + "&environment=prod")
            assert re["total"] == 0

            re = self.c.get("/log/?application=" + str(app_id) + "&environment=dev")
            assert re["total"] == 3

            # clear complete application
            re = self.c.get("/log/?application=" + str(app_id))
            assert re["total"] == 3

            re = self.c.delete("/log/?application=" + str(app_id), r_code=200)
            assert re == 3

            re = self.c.get("/log/?application=" + str(app_id))
            assert re["total"] == 0

    def test_retention_delete(self):
        sess = next(self.db_instance)

        with app_context(self, retention_days=2) as app_id:
            for i in range(5):
                sess.add(
                    LogEntry(
                        application=app_id,
                        created_at=datetime.now() - timedelta(days=i),
                        created_by_id=CURRENT_USER,
                    )
                )
            sess.commit()

            assert sess.query(LogEntry).count() == 5

            re = self.c.get("/log/?application=" + str(app_id))
            assert re["total"] == 5

            delete_old_logs(sess)

            assert sess.query(LogEntry).count() == 2

            # delete all logs
            re = self.c.delete("/log/?application=" + str(app_id), r_code=200)
