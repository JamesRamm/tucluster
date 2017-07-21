# -*- coding: utf-8 -*-
import falcon
from fmdb import connect, Model, ModelRun
from qflow.celery import app
from tucluster import resources
from tucluster.conf import settings


# Create the WSGI application. It is aliased to ``application``
# as this is what gunicorn expects.
api = application = falcon.API()

# Connect to the database
db = connect(**settings['MONGODB'])

# Add the routes
api.add_route(
    '/models',
    resources.models.ModelCollection(
        resources.models.ArchiveStore(settings['TUFLOW_DATA']),
        Model
    )
)

api.add_route(
    '/models/{name}',
    resources.models.ModelItem(Model)
)

api.add_route(
    '/runs',
    resources.runs.ModelRunCollection(ModelRun)
)

api.add_route(
    '/runs/{oid}',
    resources.runs.ModelRunItem(ModelRun)
)
