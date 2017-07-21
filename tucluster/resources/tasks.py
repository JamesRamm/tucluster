import json
import falcon
from qflow.celery import app

class TaskDetail(object):
    '''Get information about an executing task
    '''

    def on_get(self, req, resp, id):
        '''GET handler
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
