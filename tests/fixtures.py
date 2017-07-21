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
        os.makedirs(settings['TUFLOW_DATA'])
    except:
        pass
    yield testing.TestClient(api)
    # Remove the data directory after testing
    shutil.rmtree(settings['TUFLOW_DATA'])
    # Drop the test database
    db.drop_database("mongoenginetest")
