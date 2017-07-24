import uuid
import json
import os
import pathlib
import falcon
from falcon import testing
from fmdb import Model, ModelRun
from fmdb.serializers import directory_tree_serializer, id_from_path
from tucluster.conf import settings
from tucluster.resources.files import FileItem
from .fixtures import client

class FileWrapper(object):

    def __init__(self, file_like, block_size=8192):
        self.file_like = file_like
        self.block_size = block_size

    def __getitem__(self, key):
        data = self.file_like.read(self.block_size)
        if data:
            return data

        raise IndexError


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

    def test_get_folder_tree(self, client):
        '''Test we can serialize a directory tree structure
        '''
        # Get path within designated storage directory
        fid = id_from_path(settings['TUFLOW_DATA'])

        response = client.simulate_get('/tree/{}'.format(fid))
        assert response.status == falcon.HTTP_OK
        assert response.text == directory_tree_serializer(fid)

    def test_get_file(self, client):
        '''Test we can download a result file
        '''
        # Create a file in the storage path
        dirpth = pathlib.Path(settings['TUFLOW_DATA'])
        fpath = dirpth / 'test.txt'
        fpath.touch()

        # Use same encoding fmdb does to represent a file
        fid = id_from_path(str(fpath))

        # Create the download request
        response = client.simulate_get('/files/{}'.format(fid))
        assert response.status == falcon.HTTP_OK

    def test_fail_folder_tree(self, client):
        '''Test we are not allowed to access folders
        outside the allowed storage
        '''
        restricted_path = os.path.dirname(__file__)
        fid = id_from_path(restricted_path)
        response = client.simulate_get('/tree/{}'.format(fid))
        assert response.status == falcon.HTTP_BAD_REQUEST

    def test_fail_file(self, client):
        '''Test we are not allowed to access files
        outside the allowed storage
        '''
        restricted_path = os.path.abspath(__file__)
        fid = id_from_path(restricted_path)
        response = client.simulate_get('/files/{}'.format(fid))
        assert response.status == falcon.HTTP_BAD_REQUEST
