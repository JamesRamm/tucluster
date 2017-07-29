#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import uuid
import zipfile
import json
import falcon
from falcon import testing
from tucluster.fmdb import Model, ModelRun
from tucluster.conf import settings
from .fixtures import client

def create_zip():
    '''Create a random zip file with a tcf file in it
    '''
    fname = 'test.tcf'
    with open(fname, 'w') as fobj:
        fobj.write("RANDOM STATEMENT == RANDOM")
    path = os.path.join(settings['MODEL_DATA_DIR'], "{}.zip".format(uuid.uuid4()))
    with zipfile.ZipFile(path, mode='w') as zfile:
        zfile.write(fname)
    os.remove(fname)
    return path

class TestModel:

    def _create_model(self):
        return Model(name=str(uuid.uuid4())).save()

    # pytest will inject the object returned by the "client" function
    # as an additional parameter.
    def test_list_models(self, client):
        '''The API can list all ``Model`` documents in the database
        '''
        self._create_model()
        self._create_model()
        response = client.simulate_get('/models')
        queryset = Model.objects.all()
        expected = queryset.to_json()
        assert response.text == expected
        assert response.status == falcon.HTTP_OK


    def test_get_model(self, client):
        '''The API can return a single ``Model`` document
        '''
        model = self._create_model()
        response = client.simulate_get('/models/{}'.format(model.name))
        assert response.text == model.to_json()
        assert response.status == falcon.HTTP_OK

    def test_bad_get_model(self, client):
        '''Test we get an appropriate response
        if we try to get a model which doesnt exist
        '''
        response = client.simulate_get('/models/badName')
        assert response.status == falcon.HTTP_BAD_REQUEST

    def test_posted_model_gets_saved(self, client):
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
        assert response.status == falcon.HTTP_CREATED
        assert 'Location' in response.headers
        assert '_id' in response.json

    def test_create_empty_model(self, client):
        '''The API can create a ``Model`` without any data
        '''
        body = {
            'name': 'test model',
            'description': 'test model description'
        }
        response = client.simulate_post(
            '/models',
            body=json.dumps(body),
            headers={'content-type': 'application/json'}
        )
        assert response.status == falcon.HTTP_CREATED
        assert 'Location' in response.headers

    def test_post_bad_content_type(self, client):
        '''The API will reject a POST request without
        the content-type header correctly set
        '''
        body = {
            'name': 'test model',
            'description': 'test model description'
        }
        response = client.simulate_post(
            '/models',
            body=json.dumps(body)
        )
        assert response.status == falcon.HTTP_BAD_REQUEST


    def test_update_model(self, client):
        '''Test updating a ``Model``
        '''
        model = self._create_model()
        body = {
            'name': 'My Model',
            'description': 'My Model Description',
            'email': 'random@gmail.com'
        }
        response = client.simulate_patch(
            '/models/{}'.format(model.name),
            body=json.dumps(body),
            headers={'content-type': 'application/json'}
        )

        assert response.status == falcon.HTTP_NO_CONTENT

    def test_update_model_with_file(self, client):
        '''Test adding a new data file to an existing model
        '''
        model = self._create_model()
        headers = {
            'content-disposition': 'attachment; filename="random_file.tif"',
            'content-type': 'application/octet-stream'
        }
        body = b'fake-tif-bytes'
        response = client.simulate_patch(
            '/models/{}'.format(model.name),
            body=body,
            headers=headers
        )
        assert response.status == falcon.HTTP_ACCEPTED

        # Try again but without setting the filename
        headers['content-disposition'] = 'attachment'
        headers['content-type'] = 'image/tiff'
        response = client.simulate_patch(
            '/models/{}'.format(model.name),
            body=body,
            headers=headers
        )
        assert response.status == falcon.HTTP_ACCEPTED


class TestMonitoring:
    '''Test we can monitor tasks as they are running
    '''
    def test_get_task_status(self, client):
        '''Test we can get the status of a task for a model run
        '''
        run = ModelRun(
            entry_point='control2.py',
            engine='anuga'
        ).save()

        response = client.simulate_get('/tasks/{}'.format(str(run.task_id)))
        assert response.status == falcon.HTTP_OK
