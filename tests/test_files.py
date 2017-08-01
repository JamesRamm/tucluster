'''Tests for files API
'''
import os
import pathlib
import json
import falcon
from falcon import testing
from tucluster.fmdb.serializers import directory_tree_serializer, id_from_path
from tucluster.conf import settings
from tucluster.resources.files import FileItem
from .fixtures import client

class TestFiles:
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
        fid = id_from_path(settings['MODEL_DATA_DIR'])

        response = client.simulate_get('/files/tree/{}'.format(fid))
        assert response.status == falcon.HTTP_OK
        assert response.text == json.dumps(directory_tree_serializer(settings['MODEL_DATA_DIR']))

    def test_get_file(self, client):
        '''Test we can download a result file
        '''
        # Create a file in the storage path
        dirpth = pathlib.Path(settings['MODEL_DATA_DIR'])
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
        response = client.simulate_get('/files/tree/{}'.format(fid))
        assert response.status == falcon.HTTP_BAD_REQUEST

    def test_fail_file(self, client):
        '''Test we are not allowed to access files
        outside the allowed storage
        '''
        restricted_path = os.path.abspath(__file__)
        fid = id_from_path(restricted_path)
        response = client.simulate_get('/files/{}'.format(fid))
        assert response.status == falcon.HTTP_BAD_REQUEST
