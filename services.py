import endpoints
from bp_content.themes.default.handlers.models import *
from protorpc import remote
import logging
logger = logging.getLogger(__name__)
@endpoints.api(name='todoapi', version='v1', description='Todo API')
class TodoModelApi(remote.Service):

  @TodoModel.method(request_fields=('id','text','done'),path='todo', http_method='POST', name='todo.insert')
  def Insert(self, my_model):
      logger.warn("insert");
      logger.warn(my_model);
      my_model.put()
      return my_model

  @TodoModel.method(request_fields=('id',),path='todo/{id}', http_method='DELETE', name='todo.delete')
  def Delete(self,my_model):
      logger.warn("delete");
      logger.warn(my_model);
      ndb.delete_multi([my_model.key])
      return my_model

  @TodoModel.method(request_fields=('id',), path='todo/{id}', http_method='GET', name='todo.get')
  def Get(self, my_model):
    logger.warn("get");
    logger.warn(my_model);
    if not my_model.from_datastore:
      raise endpoints.NotFoundException('MyModel not found.')
    return my_model

  @TodoModel.query_method( query_fields=('text','limit', 'order', 'pageToken'),path='todo', name='todo.list')
  def List(self, query):
    return query


application = endpoints.api_server([TodoModelApi], restricted=False)