'''HTTP interface to user uploaded files and model result files
'''
import falcon
from fmdb import serializers


class FileItem(object):

    def __init__(self, data_store):
        # Instance of ``DataStore`` which encapsulates the
        # data storage location and provides access methods
        self._data_store = data_store

    def on_get(self, req, resp, fid):
        '''Return the requested file as a stream.

        Args:
            fid (str): The file id. This is a URL safe base64 representation
                of the file path. The representation can be got by first querying
                the file tree of e.g the model run 'results' folder

        Example::

                http --download localhost:8000/files/{fid}
        '''
        try:
            resp.stream, resp.stream_len, resp.content_type = self._data_store.open(fid)
        except PermissionError as error:
            resp.status = falcon.HTTP_BAD_REQUEST
            resp.body = str(error)


class Tree(FileItem):
    '''Serialize a directory tree.
    This is used to explore results folders, uploaded input folders etc.
    '''
    def on_get(self, req, resp, fid):
        ''' Return a JSON representation of the directory tree. The JSON response has the
        following attributes:

            - ``type``: file or folder
            - ``name``: The base name of the file/folder
            - ``path``: Absolute path to the object.
            - ``id``: URL-safe base64 encoding of the ``path``
            - ``children``: Only present if ``type`` is ``folder``. A list of all
                children of this folder, each having the same representation.

        Args:
            fid (str): the base64 encoded url safe ID for the path to the root folder

        Example::

            http localhost:8000/files/tree/{fid}

        '''
        try:
            self._data_store.validate_fid(fid)
            resp.status = falcon.HTTP_OK
            path = serializers.path_from_id(fid)
            resp.body = serializers.directory_tree_serializer(path)
        except PermissionError as error:
            resp.status = falcon.HTTP_BAD_REQUEST
            resp.body = str(error)
