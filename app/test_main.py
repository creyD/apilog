from creyPY.fastapi.db.session import SQLALCHEMY_DATABASE_URL, get_db
from creyPY.fastapi.models.base import Base
from creyPY.fastapi.testing import GenericClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

from app.services.auth import verify

from .main import app

CURRENT_USER = "api-key|testing"


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
