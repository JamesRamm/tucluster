#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import uuid
import zipfile
import json
import shutil
from urllib.parse import urlencode
import falcon
from falcon import testing
import pytest
from fmdb import Model, ModelRun  # noqa
# Before importing the tucluster app we must override the settings
# for testing
from tucluster.conf import settings
settings['TUFLOW_DATA'] = os.path.join(os.path.dirname(__file__), 'data')
settings['MONGODB'] = {
    "db": "mongoenginetest",
    "host": "mongomock://localhost"
}

from tucluster.app import api, db  # noqa



def create_zip():
    fname = 'test.tcf'
    with open(fname, 'w') as fobj:
        fobj.write("RANDOM STATEMENT == RANDOM")
    path = os.path.join(settings['TUFLOW_DATA'], "{}.zip".format(uuid.uuid4()))
    with zipfile.ZipFile(path, mode='w') as zfile:
        zfile.write(fname)
    os.remove(fname)
    return path


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


# pytest will inject the object returned by the "client" function
# as an additional parameter.
def test_list_models(client):
    '''The API can list all ``Model`` documents in the database
    '''
    Model(name=str(uuid.uuid4())).save(),
    Model(name=str(uuid.uuid4())).save(),
    response = client.simulate_get('/models')
    queryset = Model.objects.all()
    expected = queryset.to_json()
    assert response.text == expected
    assert response.status == falcon.HTTP_OK


def test_get_model(client):
    '''The API can return a single ``Model`` document
    '''
    model = Model(name=str(uuid.uuid4())).save()
    response = client.simulate_get('/models/{}'.format(model.name))
    assert response.text == model.to_json()
    assert response.status == falcon.HTTP_OK


def test_posted_model_gets_saved(client, monkeypatch):
    '''The API can accept a data archive, create and
        return a ``Model`` document pointing to the
    location of the extracted folder
    '''
    path = create_zip()
    with open(path, 'rb') as zfile:
        fake_zip_bytes = zfile.read()
    response = client.simulate_post(
        '/models',
        body=fake_zip_bytes,
        headers={'content-type': 'application/zip'}
    )
    print(response.json)
    assert response.status == falcon.HTTP_CREATED
    assert 'Location' in response.headers
    assert '_id' in response.json


def test_post_model_run(client):
    '''The API can start a background task to run a tuflow model
    for the given Model name and control file name

    '''
    model = Model(
        name=str(uuid.uuid4()),
        control_files=['test1.tcf', 'test2.tcf']
    ).save()
    body = {
        'controlFile': 'test1.tcf',
        'modelName': model.name,
        'mock': True
    }
    response = client.simulate_post(
        '/runs',
        body=json.dumps(body)
    )
    assert response.status == falcon.HTTP_CREATED
    assert 'Location' in response.headers


def test_post_model_run_fail(client):
    '''The API will return a bad request and error message
    if POST data is poorly formatted
    '''
    response = client.simulate_post(
        '/runs',
        body=json.dumps({
            'controlFile': 'test1.tcf'
        })
    )
    assert response.status == falcon.HTTP_BAD_REQUEST


def test_list_runs(client):
    '''The API can list all ``ModelRun`` documents
    '''
    ModelRun(
        control_file='control.tcf',
        result_folder='/some/result/folder',
        log_folder='/some/log/folder',
        check_folder='/some/check/folder'
    ).save()
    response = client.simulate_get('/runs')
    queryset = ModelRun.objects.all()
    assert response.text == queryset.to_json()
    assert response.status == falcon.HTTP_OK


def test_get_run(client):
    '''The API can return a single ``ModelRun`` document
    '''
    run = ModelRun(
        control_file='control1.tcf',
        result_folder='/some/result1/folder',
        log_folder='/some/log1/folder',
        check_folder='/some/check1/folder'
    ).save()

    response = client.simulate_get('/runs/{}'.format(str(run.id)))
    assert response.text == run.to_json()
    assert response.status == falcon.HTTP_OK
