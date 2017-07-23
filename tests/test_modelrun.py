import uuid
import json
import os
import pathlib
import falcon
from falcon import testing
from fmdb import Model, ModelRun
from fmdb.serializers import directory_tree_serializer
from tucluster.conf import settings
from .fixtures import client


class TestModelRun:
    '''Test starting model runs and retrieving the db representation
    '''
    def _create_modelrun(self):
        name = str(uuid.uuid4())
        direct = settings['TUFLOW_DATA']
        return ModelRun(
            control_file='{}.tcf'.format(name),
            result_folder='{}/{}/result'.format(direct, name),
            log_folder='{}/{}/log'.format(direct, name),
            check_folder='{}/{}/check'.format(direct, name)
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


    def _touch_files(self, path):
        '''Create the given folder and put some random files/folders in it
        For testing directory tree endpoints
        '''
        try:
            os.makedirs(path)
        except FileExistsError:
            pass
        dirpth = pathlib.Path(path)
        (dirpth / 'file.txt').touch()
        (dirpth / 'file2.txt').touch()
        subdir = dirpth / 'subdir'
        subdir.mkdir()
        (subdir / 'file1.txt').touch()
        return dirpth

    def _test_get_folder_tree(self, client, folder):

        run = self._create_modelrun()
        if folder == 'results':
            path = run.result_folder
        elif folder == 'check':
            path = run.check_folder
        elif folder == 'log':
            path = run.log_folder

        # Make the result folder and put some stuff in it
        # to test the API against
        self._touch_files(path)
        response = client.simulate_get('/runs/{}/{}'.format(str(run.id), folder))
        assert response.status == falcon.HTTP_OK
        assert response.text == directory_tree_serializer(path)

    def test_get_result_tree(self, client):
        '''The API can return the result directory tree for a model run
        '''
        self._test_get_folder_tree(client, 'results')

    def test_get_check_tree(self, client):
        '''The API can return the result directory tree for a model run
        '''
        self._test_get_folder_tree(client, 'check')

    def test_get_log_tree(self, client):
        '''The API can return the result directory tree for a model run
        '''
        self._test_get_folder_tree(client, 'log')

    def test_get_file(self, client):
        '''Test we can download a result file
        '''
        run = self._create_modelrun()
        dirpath = self._touch_files(run.result_folder)

        # Get the path to the first file in the directory
        fpath = next(x for x in dirpath.iterdir() if x.is_file())

        # Create the download request
        response = client.simulate_get('/runs/{}/results/{}'.format(run.id, fpath))
