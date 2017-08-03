'''Request handlers for ModelRun data
'''
import json
import os
import falcon
from qflow import tasks
from tucluster.fmdb import Model
from tucluster.conf import settings


class ModelRunCollection(object):

    def __init__(self, run_document):
        self._document = run_document

    def on_get(self, req, resp):
        '''Retrieve a JSON representation of all ``ModelRun`` documents.

        A ``ModelRun`` represents a single flood modelling task as executed by
        e.g. Tuflow.
        It stores metadata associated with the task, whereas the actual task results
        can be retrieved by inspecting the task itself, using the task id stored in
        the ``ModelRun``.

        A ``ModelRun`` has the following attributes:

        - ``entry_point``: The tuflow control file used in this run.
        - ``task_id``: The ID of the asynchronous task where the modelling program (tuflow)
            is being executed. This id can be used to inspect the task results by passing it
            to the ``/tasks/{id}`` endpoint.

        - ``is_baseline``: Indicates whether this run is the chosen 'baseline' for the model.
            By default, this is false and would typically be updated by a PATCH request after
            inspecting the task results.

        - ``model`` - The parent ``Model`` instance to which this run belongs.

        Example::

            http localhost:8000/runs
        '''
        # support optional filtering by entry_point and model
        entrypoint = req.get_param('entrypoint')
        model = req.get_param('model')
        kwargs = {}
        if entrypoint:
            kwargs['entry_point'] = entrypoint
        if model:
            model = Model.objects.get(name=model)
            kwargs['model'] = model

        if kwargs:
            docs = self._document.objects(**kwargs)
        else:
            docs = self._document.objects.all()

        # Create a JSON representation of the resource
        resp.body = docs.to_json()

        # The following line can be omitted because 200 is the default
        # status returned by the framework, but it is included here to
        # illustrate how this may be overridden as needed.
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        '''Create a new ``ModelRun`` which will trigger the execution of an asynchronous
         modelling task by e.g. running Tuflow.

        To create the ``ModelRun`` the post request must include a JSON object in its' body
        with the following parameters:

            - ``modelName``: The name of the parent ``Model`` instance which defines the previously
                uploaded model data.

            - ``entrypoint``: The .tcf Tuflow control file to use for the modelling task.
                A list of available control files is available by inspecting ``Model`` instances

            - ``engine``: 'tuflow' or 'anuga'. The flood modelling software to use.

            - ``mock``: Boolean value stating whether to mock the the modelling task instead
                of actually running tuflow. Mocking will cause a do-nothing task to be executed
                for ~1 min. No modelling software will be executed and no results created.
                Intented for testing purposes only.

        The response will contain a JSON representation of the resulting ``ModelRun``
        instance and the resource location will be stored in the Location header.
        '''
        doc = json.load(req.bounded_stream)
        try:
            entry_point = doc['entrypoint']
            engine = doc['engine']
            model = Model.objects.get(name=doc['modelName'])
            mock = doc.get('mock', False)

            # Start the task
            path = os.path.join(model.resolve_folder(), entry_point)
            if engine == 'tuflow':
                task = tasks.run_tuflow.delay(
                    path,
                    settings['TUFLOW_PATH'],
                    mock=mock
                )
            elif engine == 'anuga':
                task = tasks.run_anuga.delay(path, env_name=settings['ANUGA_ENV'])

            # Create the model run
            run = self._document(
                entry_point=entry_point,
                task_id=task.id,
                model=model,
                engine=engine
            ).save()

            resp.location = '/runs/{}'.format(run.id)
            resp.body = run.to_json()
            resp.status = falcon.HTTP_CREATED

        except KeyError as err:
            resp.body = str(err)
            resp.status = falcon.HTTP_BAD_REQUEST

class ModelRunItem(ModelRunCollection):

    def on_get(self, req, resp, oid):
        '''Retrieve a JSON representation of a single ``ModelRun`` from its' object id

        A ``ModelRun`` contains metadata about a modelling task.
        The results or status of the modelling task can be found by
        using the ``task_id`` attribute of the ``ModelRun`` in a call to
        the ``tasks`` resource: ``/tasks/{task_id}``

        Example::

            http localhost:8000/runs/{oid}
        '''
        doc = self._document.objects.get(id=oid)
        resp.body = doc.to_json()
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp, oid):
        resp.status = falcon.HTTP_METHOD_NOT_ALLOWED

    def on_patch(self, req, resp, oid):
        '''Update a model run to specify whether it is the baseline run.
        '''
        doc = self._document.objects.get(id=oid)
        data = json.load(req.bounded_stream)
        doc.is_baseline = data['isBaseline']
        doc.save()
        resp.status = falcon.HTTP_ACCEPTED
