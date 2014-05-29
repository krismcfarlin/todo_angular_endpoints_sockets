import endpoints
from bp_content.themes.default.handlers.models import *
from protorpc import remote
import logging
logger = logging.getLogger(__name__)

from google.appengine.api import memcache
from google.appengine.api import channel
from webapp2_extras.json import json


@endpoints.api(name='todoapi', version='v1', description='Todo API')
class TodoModelApi(remote.Service):

  @TodoModel.method(request_fields=('id','text','done'),path='todo', http_method='POST', name='todo.insert')
  def Insert(self, my_model):
      format = "%Y-%m-%d %H:%M:%S"

      user_id=self.request_state.headers.get('clientId',None)
      my_model.put()
      people=memcache.get("todo")
      if people:
          for person in people:
            if not person == user_id:
                channel.send_message("%s_%s"%(person,'todo'),json.dumps({'action':'update','id':"%s"%my_model.id,'text':my_model.text,'done':my_model.done,'created':my_model.created.strftime(format)}))
      return my_model

  @TodoModel.method(request_fields=('id',),path='todo/{id}', http_method='DELETE', name='todo.delete')
  def Delete(self,my_model):
      user_id = self.request_state.headers.get('clientId',None)

      ndb.delete_multi([my_model.key])
      people=memcache.get("todo")
      if people:
        for person in people:
            if not person == user_id:
                channel.send_message("%s_%s"%(person,'todo'),json.dumps({'action':'delete','id':"%s"%my_model.id}))
      return my_model

  @TodoModel.method(request_fields=('id',), path='todo/{id}', http_method='GET', name='todo.get')
  def Get(self, my_model):
      user_id = self.request_state.headers.get('clientId',None)
      if not my_model.from_datastore:
          raise endpoints.NotFoundException('MyModel not found.')
      return my_model

  @TodoModel.query_method( query_fields=('text','limit', 'order', 'pageToken'),path='todo', name='todo.list')
  def List(self, query):
    user_id = self.request_state.headers.get('clientId',None)
    return query


application = endpoints.api_server([TodoModelApi], restricted=False)