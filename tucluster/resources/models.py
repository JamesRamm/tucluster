import falcon


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
