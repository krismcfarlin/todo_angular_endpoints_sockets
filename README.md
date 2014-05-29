This is a permenant record of my exploration of angular with google end points.  Hopefully others will learn from my mistakes, or when I look back at this in a few months this will help jump start the process.
Ok lets go out and get everything we need.  

1.  Setup  https://github.com/krismcfarlin/todo_angular_endpoints .  Read through the README and follow the directions.
  
2.  Setup the app.yaml 

    a.  Right above the handlers section add a inboud_services section 

    ```yaml
    inbound_services:
    - channel_presence
    ```
    
    b.  In the handlers section right at the bottom make it look like below
    
    ```yaml
    - url: /_ah/channel/.*
      script: main.app
    - url: /.*
      script: main.app
    ```

3.  Setup the Handlers.  Open up bp_content/handlers/handlers.py
    
    ```python
    class ChannelConnected(BaseHandler):
        def post(self,**kwargs):
            from_person = self.request.get('from')
            (person,room)= from_person.split("_")
            memcache_key=room
            people=memcache.get(memcache_key)
            if people:
                people.append(person)
                memcache.set(room,people,3600)
            else:
                memcache.set(room,[person],3600)

    class ChannelDisconnected(BaseHandler):
        def post(self,**kwargs):
            from_person = self.request.get('from')
            (person,room)= from_person.split("_")
            memcache_key=room
            people=memcache.get(memcache_key)
            if people:
                people.remove(person)
                memcache.set(room,people,3600)
            else:
                memcache.set(room,[],3600)

    ```
    These classes handle what should be done when a client connects to the channel.   We are retrieving their id we set in the javascrpt from the room and then adding it to the memcache.  We do the same with the ChannelDisconnected except we remove them from the room list.  
    
    
    Also we need to make changes in our TestAngular Class.  You will need to change it so it looks like below.
    
    ```python
    class TestAngular(BaseHandler):
        def get(self,**kwargs):
            params = {
                'me'        : "%d"%random.randint(1,10000),
                'game_key'  : "todo"
            }
            token = channel.create_channel('%s_%s'%(params['me'],params['game_key']))
            params['token'] = token

            return self.render_template('index.html', **params)
    ```
    Here we are sending a few params to the index script.  We randomly generate a client id called me and pass it into the script as well as a room key to identify the data we are watching.  You could modify this script to hold a proper client id or api which would probably be more useful. 
    
    
4.  Lets next go into the bp_content/themes/default/routes/__init__.py  We need to add the urls for the routes to the connect and disconnect.

    ```python
    RedirectRoute('/_ah/channel/connected/', handlers.ChannelConnected,name="channelconnected",strict_slash=False),
    RedirectRoute('/_ah/channel/disconnected/', handlers.ChannelDisconnected,name="channeldisconnected",strict_slash=False), 
    ```
    
5.  Next we will need to make a change to the security setting of the BaseHandler or the POST data sent to the connect and disconnect will be ignored.  So we will need to open bp_includes/lib/basehandler.py
    ```python
    if self.request.method == "POST" and not self.request.path.startswith('/taskqueue'):
    #changed to
    if self.request.method == "POST" and not self.request.path.startswith('/taskqueue') and not self.request.path.startswith('/_ah'):
    ```
    Normally we block all POSTs to the system that don't have valid CSRF token.  We need to make an exception so the connect and disconnect will work.

6.  Next we will take a look at the index.html file found bp_content/themes/default/templates/index.html
    
    
    ```python
    {% raw %}
    <label ng-dblclick="editTodo(todo)">{{todo.text}}</label>
	{% endraw %}
	
	{% raw %}
    <span id="todo-count"><strong>{{remaining()}}</strong>
            <ng-pluralize count="remaining()" when="{ one: 'item left', other: 'items left' }"></ng-pluralize>
    </span>
    {% endraw %}
    
    {% raw %}
        <button id="clear-completed" ng-click="clearCompletedTodos()" ng-show="completedCount()">Clear completed ({{completedCount()}})</button>
    {% endraw %}
    ```
    At line 34-37, 50-54, 55-57 we added the {% raw %} tags around the angular template.  Instead of surrounding the whole file, this time we do need to use some of the jinga2 templating so we are going to be more selective on the parts we mark as raw. 
    
    ```python
    <script>
        window.token = "{{token}}";
        window.client_id = {{me}};
	</script>
	```
	
	At line 68 we add a small js code section that defines the token we are going to use for the channel and the id of the client.  We need both in the angular section start up so messages will be sent from the server to the client. 
	
	```python
	<script type="text/javascript" src="/_ah/channel/jsapi"></script>
    ```
    
    At line 76 we add a js file import that will give us access to communicate to the GAE channel.  
    
    
7.  Next we will modify bp_content/themes/default/static/js/controllers/todoCtrl.js so that the todoCtrl is using the channel data and is updated in real time.
    ```python
    app.factory('todoFactory', function($resource) {
        var apiRoot='//' + window.location.host + '/_ah/api/todoapi/v1/todo/:id';
        return $resource(apiRoot, {},{
            save:   {
                method: 'POST',
                headers:{clientId : window.client_id}
            },
            delete: {
                method: 'DELETE',
                headers: {clientID: window.client_id}
            },
            update: {
                method: 'PUT',
                headers:{clientId : window.client_id}
            },
            query:  {
                method:'GET',
                isArray:true,
                headers:{clientId : window.client_id},
                transformResponse: function(data, headers){
                    console.log(data);
                    return JSON.parse(data)['items'];
                }
            }


        });
    });
    ```
    We have made a few changes to the factory used to get all the information to and from the server.  We want to send a clientId with the headers so the server has a way of identifying the user.  In the original version of this script this was handled by cookies, but we decided to move it to an explicit placement in the headers of the calls.  
    
    ```python
    var channel = new goog.appengine.Channel(window.token);
    var socket = channel.open();
    socket.onmessage=function(message){
        json=JSON.parse(message['data']);
        if (json.action =="update"){
            temp = _.find($scope.todos,function(todo){ console.log(todo.id);return todo.id == json.id  });
            if (temp == undefined){
                newTodo = new todoFactory({id:json.id,text:json.text, done:json.done});
                $scope.todos.push(newTodo);
            } else {
                temp.text= json.text;
                temp.done= json.done;
            }
        }
        if (json.action == "delete"){
            $scope.todos=_.filter($scope.todos,function(todo){ console.log(todo.id);return todo.id != json.id })
        }
        $scope.$apply()
    }
    ```
    Here we are making changes for receiving information from the server. 
    
    Lets break it down

    
    ```python
    var channel = new goog.appengine.Channel(window.token);
    var socket = channel.open();
    ```
    Here we are starting up a new channel and making a connection to the server.  
    
    
    ```python
        if (json.action =="update"){
            temp = _.find($scope.todos,function(todo){ console.log(todo.id);return todo.id == json.id  });
            if (temp == undefined){
                newTodo = new todoFactory({id:json.id,text:json.text, done:json.done});
                $scope.todos.push(newTodo);
            } else {
                temp.text= json.text;
                temp.done= json.done;
            }
        }
    ```
    Here we are testing to see if the server is sending us an update action.  If the sever is sending us an update we look for the todo in the todos list.  If we find it we alter the data with the data sent with the call to update.  If we don't find a todo with the same id we add a new toodo with that id. 

    
    ```python
        if (json.action == "delete"){
            $scope.todos=_.filter($scope.todos,function(todo){ console.log(todo.id);return todo.id != json.id })
        }
    ```
    Here we are testing to see if the server is sending us a delete action.  If the server is sending us a delete action we find the todo in our todos list by its id and filter it out of the list. 
    
    
8.  The services.py file has had a number of changes.  

```python
from google.appengine.api import memcache
from google.appengine.api import channel
from webapp2_extras.json import json

```
First we added a bunch of files to be imported.  We need import: memcache for keeping track of who is still connected and who needs to be updated when data is changed.  channel to send the update message to the client.  json to decode/encode the data being sent to and from the client. 
    

```python  
      user_id = self.request_state.headers.get('clientId',None)
      people=memcache.get("todo")
      if people:
          for person in people:
            if not person == user_id_:
                channel.send_message("%s_%s"%(person,'todo'), json.dumps({'action':'update', 'id':my_model.id, 'text':my_model.text, 'done':my_model.done, 'created':my_model.created.strftime(format)}))
```
We get all the people who have connected using the ChannelConnected class from the memcache.  If there are people in the memcache we loop through them sending a message that their data needs to be updated, we do this for everyone except the person who changed the data.

If you want to see this working.  Open different browsers to https://todo-angular-endpoints-socket.appspot.com/  

And we are done!

I am thinking the next expansion on this code will be a tutorial going over how to hook up an iphone up to a gae channel.  Stay tuned!


 
    
    
    