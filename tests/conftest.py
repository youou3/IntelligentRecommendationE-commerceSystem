import pytest
import mongomock

from app import create_app
from app.core.config import TestingConfig
from app.core.database import db


@pytest.fixture
def app(monkeypatch):
    app = create_app(TestingConfig)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True

    mock_client = mongomock.MongoClient()
    mock_db = mock_client[app.config['MONGO_DB_NAME']]

    import app.core.database as database_module
    database_module.mongo_client = mock_client
    database_module.mongo_db = mock_db

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
