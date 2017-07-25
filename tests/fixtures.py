import os
import shutil
import pytest
from falcon import testing

from tucluster.conf import settings
from tucluster.app import api, db


@pytest.fixture
def client():
    # Make sure the data directory exists
    # before we start making test files in it
    try:
        os.makedirs(settings['MODEL_DATA_DIR'])
    except:
        pass
    yield testing.TestClient(api)
    # Remove the data directory after testing
    shutil.rmtree(settings['MODEL_DATA_DIR'])
    # Drop the test database
    db.drop_database("mongoenginetest")
