'''Tests for Runs api
'''
import uuid
import json
import os
import falcon
from falcon import testing
from tucluster.fmdb import Model, ModelRun
from tucluster.conf import settings
from .fixtures import client


class TestModelRun:
    '''Test starting model runs and retrieving the db representation
    '''
    def _create_modelrun(self):
        name = str(uuid.uuid4())
        direct = settings['MODEL_DATA_DIR']
        return ModelRun(
            control_file='{}.tcf'.format(name),
        ).save()


    def test_post_model_run(self, client):
        '''The API can start a background task to run a tuflow model
        for the given Model name and control file name
        '''
        model = Model(
            name=str(uuid.uuid4()),
            control_files=['test1.tcf', 'test2.tcf'],
            folder=os.path.dirname(__file__)
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


    def test_post_model_run_fail(self, client):
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


    def test_list_runs(self, client):
        '''The API can list all ``ModelRun`` documents
        '''
        self._create_modelrun()
        response = client.simulate_get('/runs')
        queryset = ModelRun.objects.all()
        assert response.text == queryset.to_json()
        assert response.status == falcon.HTTP_OK


    def test_get_run(self, client):
        '''The API can return a single ``ModelRun`` document
        '''
        run = self._create_modelrun()
        response = client.simulate_get('/runs/{}'.format(str(run.id)))
        assert response.text == run.to_json()
        assert response.status == falcon.HTTP_OK

    def test_patch_run(self, client):
        '''The API will update a model run to set it as the
        baseline model.
        '''
        run = self._create_modelrun()
        response = client.simulate_patch(
            '/runs/{}'.format(str(run.id)),
            body=json.dumps({
                'isBaseline': True
            })
        )
        assert response.status == falcon.HTTP_ACCEPTED
