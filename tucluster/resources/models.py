import uuid
import mimetypes
import os
import io
import falcon

from qflow.utils import extract_model, ensure_dir


class ModelCollection(object):
    '''List and create ``Model`` documents
    '''

    def __init__(self, archive_store, model_document):
        # Instance supporting `save()` which will handle writing
        # incoming zip data streams to disk
        self._archive_store = archive_store

        # MongoEngine ``Document`` class which provides the data for this
        # resource
        self._document = model_document

    def on_get(self, req, resp):
        '''GET handler
        '''
        docs = self._document.objects.all()
        # Create a JSON representation of the resource
        resp.body = docs.to_json()
        resp.status = falcon.HTTP_OK

    def on_post(self, req, resp):
        '''POST handler
        '''
        directory, name = self._archive_store.save(req.stream, req.content_type)
        # Create the model
        model = self._document(
            name=name,
            folder=directory
        ).save()

        resp.status = falcon.HTTP_CREATED
        resp.location = '/models/{}'.format(model.name)
        resp.body = model.to_json()

class ModelItem(object):
    '''Fetch or update a single ``Model`` document
    '''
    def __init__(self, model_document):
        # MongoEngine ``Document`` class which provides the data for this
        # resource
        self._document = model_document

    def on_get(self, req, resp, name):
        '''GET handler
        '''
        model = self._document.objects.get(name=name)
        resp.status = falcon.HTTP_OK
        resp.body = model.to_json()


class ArchiveStore(object):
    '''Save and extract a zip file from a stream
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
