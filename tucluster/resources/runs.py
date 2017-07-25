import json
import os
import falcon
from qflow import tasks
from fmdb import Model, serializers
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

        - ``control_file``: The tuflow control file used in this run.
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

            - ``controlFile``: The .tcf Tuflow control file to use for the modelling task.
                A list of available control files is available by inspecting ``Model`` instances

            - ``tuflowExe``: Optional. The full path of an available tuflow (or otherwise)
                executable to run against the chosen control file. Available executables
                are configured (by the site admin).
                in the settings file given to tucluster. If not provided, this will default to the
                first available executable. [I.e. if only one executable has been configured, this
                option can be safely omitted]

            - ``mock``: Boolean value stating whether to mock the the modelling task instead
                of actually running tuflow. Mocking will cause a do-nothing task to be executed
                for ~1 min. No modelling software will be executed and no results created.
                Intented for testing purposes only.

        The response will contain a JSON representation of the resulting ``ModelRun``
        instance and the resource location will be stored in the Location header.
        '''
        doc = json.load(req.bounded_stream)
        try:
            control_file = doc['controlFile']
            model = Model.objects.get(name=doc['modelName'])
            tuflow_exe = doc.get(
                'tuflowExe', next(iter(settings['TUFLOW_EXES'].values())))
            mock = doc.get('mock', False)

            # Start the task
            task = tasks.run_tuflow.delay(
                os.path.join(model.resolve_folder(), control_file),
                tuflow_exe,
                mock=mock
            )

            # Create the model run
            run = self._document(
                control_file=control_file,
                task_id=task.id,
                model=model
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
        resp.status = falcon.HTTP_400

    def on_patch(self, req, resp, oid):

        doc = self._document.objects.get(id=oid)
        data = json.load(req.bounded_stream)
        doc.is_baseline = data['isBaseline']
        doc.save()
        resp.status = falcon.HTTP_ACCEPTED
