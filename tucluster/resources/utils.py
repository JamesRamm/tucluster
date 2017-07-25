'''User data storage access methods
'''
import uuid
import mimetypes
import os
import io
import fmdb
from qflow.utils import extract_model, ensure_dir


class DataStore(object):
    '''Data storage and retrieval for all user uploaded files.
    An instance of ``DataStore`` is the interface to the location of all modelling
    inputs and results.
    '''
    _CHUNK_SIZE_BYTES = 4096

    def __init__(self, storage_path, uuidgen=uuid.uuid4, fopen=io.open):
        # Dependency injection used so monkeypatching can be avoided if needed
        self._storage_path = storage_path
        self._uuidgen = uuidgen
        self._fopen = fopen

    def save(self, stream, content_type):
        '''Save the stream to disk and extract its contents
        '''
        # Make sure the storage path exists
        ensure_dir(self._storage_path)

        ext = mimetypes.guess_extension(content_type)
        name = str(self._uuidgen())
        fname = '{uuid}{ext}'.format(uuid=name, ext=ext)
        archive_path = os.path.join(self._storage_path, fname)

        with self._fopen(archive_path, 'wb') as archive:
            while True:
                chunk = stream.read(self._CHUNK_SIZE_BYTES)
                if not chunk:
                    break

                archive.write(chunk)

        # extract the zip file
        directory = extract_model(archive_path, name, self._storage_path)
        return directory, name

    def open(self, fid):
        '''Open the file path given by its' fid and return the stream
        '''
        filepath = self.validate_fid(fid)

        stream = self._fopen(filepath, 'rb')
        stream_len = os.path.getsize(filepath)
        content_type = mimetypes.guess_type(filepath)[0]

        return stream, stream_len, content_type

    def validate_fid(self, fid):
        '''Validate a url-safe base64 encoding of a file or folder path on the server.

        This ensures only paths within the configured storage location are
        accessible.

        Args:

            fid (str): URL-safe base64 encoding of a filepath. A HTTP client typically
            would not encode the path itself, but retrieve fids' for valid file paths
            from other tucluster endpoints. For example, the ``/models`` endpoint will
            return a list of ``Model`` representations, each having a ``folder`` attribute
            which is the encoded folder path to where the input data is stored.

        Returns:

            str: The decoded file/folder path if FID was valid.

        Raises:

            PermissionError: Raise if the FID is invalid. I.e the decoded path lies outside
            the configured storage location
        '''
        # decode the file id
        filepath = fmdb.path_from_id(fid)

        # Ensure that the file path is within the storage directory
        # to prevent clients from downloading OS and private files
        if self._storage_path not in filepath:
            raise PermissionError('You do not have permission to access this file')

        return filepath
