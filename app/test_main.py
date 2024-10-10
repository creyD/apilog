from creyPY.fastapi.db.session import SQLALCHEMY_DATABASE_URL, get_db
from creyPY.fastapi.models.base import Base
from creyPY.fastapi.testing import GenericClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

from app.services.auth import verify
import contextlib
from .main import app

CURRENT_USER = "api-key|testing"


@contextlib.contextmanager
def app_context(self):
    app_id = self.create_app()
    try:
        yield app_id
    finally:
        self.destroy_app(app_id)


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

        app.dependency_overrides[get_db] = get_db_test
        app.dependency_overrides[verify] = get_test_sub
        self.c = GenericClient(app)

    def teardown_class(self):
        drop_database(self.engine.url)

    def test_swagger_gen(self):
        re = self.c.get("/openapi.json")
        assert re["info"]["title"] == "ApiLog API"

    def test_health_check(self):
        self.c.get("/", parse_json=False)

    def test_application_api(self):
        self.c.obj_lifecycle({"name": "Testing"}, "/app/")

    def create_app(self):
        re = self.c.post("/app/", {"name": "Testing"})
        return re["id"]

    def destroy_app(self, app_id):
        self.c.delete(f"/app/{app_id}")

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
            assert re["object_reference"] == None
            assert re["previous_object"] == None
            assert re["created_by_id"] == CURRENT_USER

            self.c.delete(f"/log/{log_id}")
