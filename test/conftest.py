import pytest
from app import create_app
from extensions import db
from config import TestConfig
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app()
    flask_app.config.from_object(TestConfig)

    with flask_app.test_client() as testing_client:
        with flask_app.app_context():
            # logger.info("Creating all tables in test database...")
            db.create_all()
            # logger.info("Tables created.")
        yield testing_client
        with flask_app.app_context():
            # logger.info("Dropping all tables in test database...")
            db.drop_all()
            # logger.info("Tables dropped.")/
