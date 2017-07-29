# -*- coding: utf-8 -*-
import falcon
from tucluster.fmdb import connect, Model, ModelRun

# Import the celery app to ensure it is initialised when we start the server
from qflow.celery import app
from tucluster import resources
from tucluster.conf import settings

# Create the WSGI application. It is aliased to ``application``
# as this is what gunicorn expects.
api = application = falcon.API()

# Connect to the database
db = connect(**settings['MONGODB'])

# The data store encapsulates saving and retrieving files from
# the configured storage location and is used by various resources
data_store = resources.utils.DataStore(settings['MODEL_DATA_DIR'])

# Add the routes
api.add_route(
    '/models',
    resources.models.ModelCollection(
        data_store,
        Model
    )
)

api.add_route(
    '/models/{name}',
    resources.models.ModelItem(data_store, Model)
)

api.add_route(
    '/runs',
    resources.runs.ModelRunCollection(ModelRun)
)

api.add_route(
    '/runs/{oid}',
    resources.runs.ModelRunItem(ModelRun)
)

api.add_route(
    '/tasks/{id}',
    resources.tasks.TaskDetail()
)

api.add_route(
    '/files/{fid}',
    resources.files.FileItem(data_store)
)

api.add_route(
    '/files/tree/{fid}',
    resources.files.Tree(data_store)
)
