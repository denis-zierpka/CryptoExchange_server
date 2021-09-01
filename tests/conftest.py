import pytest
import sqlalchemy as sa

from app import app
from app.database import Base, Session


@pytest.fixture()
def client():
    return app.flask_app.test_client()


@pytest.fixture(autouse=True)
def _init_db():
    engine = sa.create_engine('sqlite:///test_database.db')
    Session.configure(bind=engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)
