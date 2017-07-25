import json
import falcon


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
        directory, name = self._data_store.save(req.stream, req.content_type)
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

            http localhost:8000/model/{name}
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
        data = json.load(req.bounded_stream)
        if 'description' in data:
            model.description = data['description']
        if 'name' in data:
            model.name = data['name']
        if 'email' in data:
            model.set_user(data['email'])
        model.save()
        resp.status = falcon.HTTP_NO_CONTENT
