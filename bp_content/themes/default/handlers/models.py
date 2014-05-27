from endpoints_proto_datastore.ndb import EndpointsModel
from google.appengine.ext import ndb

class TodoModel(EndpointsModel):
  _message_fields_schema = ('id', 'text','done', 'created')
  text = ndb.StringProperty()
  done = ndb.BooleanProperty()
  created = ndb.DateTimeProperty(auto_now_add=True)