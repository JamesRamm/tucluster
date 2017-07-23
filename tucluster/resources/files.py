'''HTTP interface to user uploaded files and model result files
'''
import falcon

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
        '''
        try:
            resp.stream, resp.stream_len, resp.content_type = self._data_store.open(fid)
        except PermissionError as error:
            resp.status = falcon.HTTP_BAD_REQUEST
            resp.body = str(error)
