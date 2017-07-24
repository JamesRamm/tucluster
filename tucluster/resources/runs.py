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
        docs = self._document.objects.all()

        # Create a JSON representation of the resource
        resp.body = docs.to_json()

        # The following line can be omitted because 200 is the default
        # status returned by the framework, but it is included here to
        # illustrate how this may be overridden as needed.
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp):
        '''Start a Tuflow modelling task
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
                os.path.join(model.folder, control_file),
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
        doc = self._document.objects.get(id=oid)
        resp.body = doc.to_json()
        resp.status = falcon.HTTP_200

    def on_post(self, req, resp, oid):
        resp.status = falcon.HTTP_NOT_ALLOWED
