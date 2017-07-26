import json
import falcon

class UserCollection(object):
    '''List and create users
    '''
    def __init__(self, model_document):
        self._document = model_document

    def on_get(self, req, resp):
        docs = self._document.objects.all()
        resp.body = docs.to_json()
        resp.status = falcon.HTTP_OK

    def on_post(self, req, resp):
        data = json.load(req.bounded_stream)
        try:
            user = self._document(
                email=data['email']
            ).save()

            resp.body = user.to_json()
            resp.status = falcon.HTTP_CREATED
        except KeyError:
            resp.body = "Missing 'email' attribute"
            resp.status = falcon.HTTP_BAD_REQUEST
