import json
import mimetypes
import os
import uuid
import falcon
from tucluster import fmdb


class ModelCollection(object):
    '''List and create ``Model`` documents
    '''
    def __init__(self, data_store, model_document):
        # Instance supporting `save()` which will handle writing
        # incoming zip data streams to disk
        self._data_store = data_store

        # MongoEngine ``Document`` class which provides the data for this
        # resource
        self._document = model_document

    def on_get(self, req, resp):
        '''Retrieve a JSON representation of all ``Model`` documents.

        Broadly, a ``Model`` represents a geographical domain over which we will
        produce one or more flood models (called 'runs').
        A model has a name, description and a folder where input data files are stored.
        The JSON representation returned by this GET handler encodes the folder path as
        a URL-safe base64 string which can be used with the ``/file/tree/{fid}`` endpoint.

        A ``Model`` will typically have a 'baseline' where one of the runs is selected
        as the definitive or primary flood model.

        Example::

            http localhost:8000/models
        '''
        docs = self._document.objects.all()
        # Create a JSON representation of the resource
        resp.body = docs.to_json()
        resp.status = falcon.HTTP_OK

    def on_post(self, req, resp):
        '''Create a new ``Model`` by uploading a zip file containing the input data
        required to run the model using a supported flood modelling software.

        The zip file will be saved and unpacked to the data folder configured in the
        ``data_store`` instance. This folder path will be stored in the ``Model`` instance.

        The name of the model is generated automatically and can be overwritten with a PUT
        request.

        A JSON representation of the created model is returned in the response body and
        the GET URL in the response location header.

        Example::

            http post localhost:8000/models @/path/to/my/archive.zip
        '''
        if req.content_type == 'application/json':
            # Create a model without data.
            data = json.load(req.bounded_stream)
            model = self._document(
                name=data['name']
            )
            if 'description' in data:
                model.description = data['description']
            if 'email' in data:
                model.email = data['email']
            model.save()

            resp.status = falcon.HTTP_CREATED
            resp.location = '/models/{}'.format(model.name)
            resp.body = model.to_json()

        elif req.content_type == 'application/zip':
            directory, name = self._data_store.save_zip(req.stream, req.content_type)
            # Create the model
            model = self._document(
                name=name,
                folder=directory
            ).save()

            resp.status = falcon.HTTP_CREATED
            resp.location = '/models/{}'.format(model.name)
            resp.body = model.to_json()
        else:
            resp.status = falcon.HTTP_BAD_REQUEST
            resp.body = 'Content type must be zip or json'

class ModelItem(ModelCollection):
    '''Fetch or update a single ``Model`` document
    '''
    def get_object(self, name):
        try:
            return self._document.objects.get(name=name)
        except self._document.DoesNotExist:
            raise falcon.HTTPBadRequest(
                description="A model with the name {} does not exist".format(name)
            )

    def on_get(self, req, resp, name):
        '''Retrieve a JSON representation of a single ``Model`` based on its'
        name.

        Example::

            http localhost:8000/models/{name}
        '''
        model = self.get_object(name)
        resp.status = falcon.HTTP_OK
        resp.body = model.to_json()

    def on_patch(self, req, resp, name):
        '''Update a ``Model`` instance with new data.

        Data is submitted as a JSON object. Any of the following attributes are accepted:

        - ``description``: A new description of the model
        - ``name``: A new name for the model
        - ``email``: Email address of an existing user to transfer ownership
            of the model to.

        '''
        model = self.get_object(name)
        if req.content_type == 'application/json':
            data = json.load(req.bounded_stream)
            if 'description' in data:
                model.description = data['description']
            if 'name' in data:
                model.name = data['name']
            if 'email' in data:
                model.email = data['email']

            try:
                model.save()
                resp.status = falcon.HTTP_NO_CONTENT
            except fmdb.NotUniqueError:
                resp.status = falcon.HTTP_BAD_REQUEST
                resp.body = 'Name {} is already taken'.format(data['name'])

        else:
            if model.folder:
                folder = model.resolve_folder()
            else:
                folder = model.name

            if req.content_type == 'application/zip':
                # Extract any uploaded zip file into the model data folder
                root, name = self._data_store.save_zip(req.stream, req.content_type, folder)
            else:
                # Save a single uploaded file to the model folder.
                # If the filename is given, use that, otherwise
                # try to guess the file type and generate a name
                disp = req.get_header('content-disposition')
                result = disp.split('filename=')
                if len(result) == 2:
                    filename = result[1].replace('"', '').replace("'", '')
                else:
                    ext = mimetypes.guess_extension(req.content_type)
                    filename = '{}{}'.format(uuid.uuid4(), ext)
                root, fid = self._data_store.save(req.stream, folder, filename)
                resp.body = json.dumps({
                    'fid': fid
                })


            model.folder = root
            model.save()
            resp.status = falcon.HTTP_ACCEPTED
