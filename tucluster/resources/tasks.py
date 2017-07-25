import json
import falcon
from qflow.celery import app

class TaskDetail(object):
    '''Get information about an executing task
    '''
    def on_get(self, req, resp, id):
        '''Retrive a JSON representation of a tasks' results.

        A single ``task`` is an asynchronous operation which executes
        a flood modelling program against a set of input data.

        The exact JSON returned by this call depends on the status of the
        long-running task.
        If the ``state`` is ``SUCCESS``, then the ``data`` attribute will contain
        the path location of the ``results``, ``check`` and ``log`` folders for the Tuflow
        model, encoded as url-safe base64 strings. These can be passed to the ``/files/tree/{fid}``
        endpoint to retrieve a JSON repesentation of the result folders.

        A ``FAILURE`` state will contain and error message in the ``data`` attribute.

        Further states may be:

        ``PENDING``: The task is queued and not yet started.
        ``STARTED``: The task has just started.

        Example:

            http localhost:8000/tasks/{task_id}

        '''
        result = app.AsyncResult(id)

        if result.state == 'FAILURE':
            data = str(result.result)
        else:
            data = result.result

        resp.body = json.dumps({
            'state': result.state,
            'data': data
        })
        resp.status = falcon.HTTP_OK
