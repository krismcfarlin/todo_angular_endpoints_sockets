This is a permenant record of my exploration of angular with google end points.  Hopefully others will learn from my mistakes, or when I look back at this in a few months this will help jump start the process.
Ok lets go out and get everything we need.  

I.Setup

  1. https://github.com/coto/gae-boilerplate
Read the readme ad follow the instruction on how to setup your machine and get it up and running.  I realize this is overkill for a quick little project, but who knows maybe I will add to this project in the future. ;)

  2. https://github.com/GoogleCloudPlatform/endpoints-proto-datastore .   Go clone that project as well, as it will help with writting our endpoints.  Take a look at the examples directory.

     copy the endpoints_proto_datastore into the root of your project directory.

  3.  https://github.com/tastejs/todomvc.git .  Go clone that project as we will need the  directory as a starting point.


II.Setup Model

  1. We need to set up the model for storing the data from the website.  This is done very easily using the endpoints_porot_datastore

    Go into your project and  look in the bp_content folder(where all you content should go) and find the themes directory. The project would prefer you to create a new theme for your project under this folder and use the default as an example.  I prefer to just use the default!  Under bp_content/themese/default/handlers you will find the model.py file which will contain the models for this project.

    I am going to put:

    ```python
    from endpoints_proto_datastore.ndb import EndpointsModel
    from google.appengine.ext import ndb
    
    class TodoModel(EndpointsModel):
        _message_fields_schema = ('id', 'text','done', 'created')
        text = ndb.StringProperty()
        done = ndb.BooleanProperty()
        created = ndb.DateTimeProperty(auto_now_add=True)
    ```
  2. I am including the EndpointsModel from our second project and the standard ndb models from google. I am going to add three fields to the db.

       	text		:  to hold what I am going to do
 	   	done		:  a boolean to hold if it is done
	   	created		:  a date when it was created so I can see how much I procrastinate

  3.  Also notice the _message_fields_schema, this set which fields are outputted in your calls.

III.Setup Service

  1.  Open up the app.yaml file.  
	a.  Find the handlers section and make it look like this:	
	    
	```yaml
	handlers:
        - url: /_ah/spi/.*
	        script: services.application	
	        ...
	        more handlers here, don't change.
	        ...
	```
	        
	b.  For handling the todomvc java/css you need to add some more handlers
	```yaml
		- url: /js/(.*\.js)$
          mime_type: text/javascript
          static_files: bp_content/themes/default/static/js/\1
          upload: bp_content/themes/default/static/js/(.*\.js)$

		- url: /bower_components
  	  	  static_dir: bp_content/themes/default/static/js/bower_components
    ```
    
	b.  Find the libraries section and add
	
	```yaml
	- name: endpoints
  	  version: "latest"
    ```
  
  2.  Create a new Service services.py in the root of your project folder.  


  ```python
	import endpoints
	from bp_content.themes.default.handlers.models import *
	from protorpc import remote

	@endpoints.api(name='todoapi', version='v1', description='Todo API')
	class TodoModelApi(remote.Service):

  	@TodoModel.method(request_fields=('id','text','done'),path='todo', http_method='POST', name='todo.insert')
  	def Insert(self, my_model):
    	my_model.put()
      	return my_model

  	@TodoModel.method(request_fields=('id',),path='todo/{id}', http_method='DELETE', name='todo.delete')
  	def Delete(self,my_model):
    	ndb.delete_multi([my_model.key])
      	return my_model

  	@TodoModel.method(request_fields=('id',), path='todo/{id}', http_method='GET', name='todo.get')
  	def Get(self, my_model):
    	if not my_model.from_datastore:
      	raise endpoints.NotFoundException('MyModel not found.')
    	return my_model

  	@TodoModel.query_method(query_fields=('text','limit', 'order', 'pageToken'),path='todo', name='todo.list')
  	def List(self, query):
    	return query


	application = endpoints.api_server([TodoModelApi], restricted=False)
  ```


Lets go over this:

  a.  Import everything we need from the endpoints libraries  

    	import endpoints
    	from protorpc import remote

  b.  Import the model we created earlier

    	from bp_content.themes.default.handlers.models import *

  c.  Create a Api named todoapi with a version of v1 and a description of 'Todo API'.

    	@endpoints.api(name='todoapi', version='v1', description='Todo API')
    	class TodoModelApi(remote.Service):


  d.  Create a method that can take 'id','text','done' as a request parameter.  The path of the request will be todo and can only be a POST.   It has a name of todo.insert.
    
  		@TodoModel.method(request_fields=('id','text','done'),path='todo', http_method='POST', name='todo.insert')
      	def Insert(self, my_model):

  e.  The library automagically fills out the model with id, text and done that were sent and is put below and return a json representation of this model.

		my_model.put()
		return my_model

  f.  Notice the path includes a id which needs to be sent when deleting a entry.  Also the http_method must be a DELETE

		@TodoModel.method(request_fields=('id',),path='todo/{id}', http_method='DELETE', name='todo.delete')
      	def Delete(self,my_model):
          ndb.delete_multi([my_model.key])
          return my_model

  g.  Notice that a get that include an id in the path returns a signle entry.   Also the http_method must be a GET

      	@TodoModel.method(request_fields=('id',), path='todo/{id}', http_method='GET', name='todo.get')
      	def Get(self, my_model):
        	if not my_model.from_datastore:
          	raise endpoints.NotFoundException('MyModel not found.')
        	return my_model
  h.  Notice that a get that doesn't include an id will list all entries in the db.

      	@TodoModel.query_method(query_fields=('text','limit', 'order', 'pageToken'),path='todo', name='todo.list')
      	def List(self, query):
        	return query
    	application = endpoints.api_server([TodoModelApi], restricted=False)



  3.  Experimenting With what we have built.  Please run the application and point your browser and the local url/port .  In my case it is localhost:8080/_ah/api/explorer.  This should take you to GAE api explorer.  From here we will be able to test out that our api is working correctly.   

    a.  Go down and click the insert function then fill out the form
    
    b.  Notice that a request was generated for you

    		Http://localhost:8080/_ah/api/todoapi/v1/todo POST 
    		Content-Type: application / json 
    		X-JavaScript-User-Agent: Google APIs Explorer
     
    		{
    		"Text": "clean my shoes" ,
    		"Done": true
    		}
 

	c.  Notice that a response was returned.

     
    		200 OK
     
    		- Show headers -
      
    		{
    		"Created": "2014-05-01T21: 40:12.045030" ,
    		"Done": true ,
    		"Id": "6192449487634432" ,
    		"Text": "clean my shoes"
    		}

    d.  Now try out the list function  

        You should get back something that looks like this.  Maybe not as many as I was adding todos.

 
    		200 OK
     
    		- Show headers -
      
    		{
     			"Items": [
      			{
       				"Created": "2014-05-01T21: 40:01.191850" ,
       				"Done": false ,
       				"Id": "5066549580791808" ,
       				"Text": "clean my shoes"
      			},
      			{
       				"Created": "2014-05-01T21: 38:44.942546" ,
       				"Id": "5629499534213120" ,
       				"Text": "clean my shoes"
      			},
      			{
       				"Created": "2014-05-01T21: 40:12.045030" ,
       				"Done": true ,
       				"Id": "6192449487634432" ,
       				"Text": "clean my shoes"
      			}
     			]
    		}


Go experiment with a couple of the other functions.



IV.  Onto the client side.  

1. Setup the index.html file. Copy the index file from template folder over to the bp_content/themes/default/templates directory.  We will need to make a modification to this file as the templating from GAE boilerplate doesn't play well with angular.  At the top of the file add {% raw %} and at the bottom add {% endraw %}

	Change the html section to read:

    	<html lang="en" ng-app="todomvc">

	After the <head>  add:

    	<script src="//ajax.googleapis.com/ajax/libs/angularjs/1.2.15/angular.js"></script>
    	<script src="//ajax.googleapis.com/ajax/libs/angularjs/1.2.15/angular-resource.js"></script>
    	<script src="//cdnjs.cloudflare.com/ajax/libs/underscore.js/1.6.0/underscore-min.js"></script>

	Change the body tag to:
    
    	<body ng-controller="TodoCtrl">
	
	Change in the <section id="todoapp" ...
    
    	<header id="header">
    		<h1>todos</h1>
    		<form id="todo-form" ng-submit="addTodo()">
    			<input id="new-todo" placeholder="What needs to be done?" ng-model="newTodo" autofocus>
    		</form>
    	</header>
Change in the <section id = "main"

    	<section id="main"  ng-show="todos.length" ng-cloak>
    	<input id="toggle-all" type="checkbox" ng-model="allChecked" ng-click="markAll(allChecked)">
    	<label for="toggle-all">Mark all as complete</label>
    	<ul id="todo-list">
    		<li ng-repeat="todo in todos | filter:statusFilter track by $index" ng-class="{completed: todo.done, editing: todo == editedTodo}">
    		<div class="view">
    			<input class="toggle" type="checkbox" ng-model="todo.done" ng-change="change(todo)">
    			<label ng-dblclick="editTodo(todo)">{{todo.text}}</label>
    			<button class="destroy" ng-click="removeTodo(todo)"></button>
    		</div>
    		<form ng-submit="doneEditing(todo)">
    			<input class="edit" ng-trim="false" ng-model="todo.text" ng-blur="doneEditing(todo)" todo-focus="todo == editedTodo">
    		</form>
    		</li>
    	</ul>
    	</section>

	Change in the footer id = "footer"

    	<footer id="footer"  ng-show="todos.length" ng-cloak>
    	<span id="todo-count"><strong>{{remaining()}}</strong>
    		<ng-pluralize count="remaining()" when="{ one: 'item left', other: 'items left' }"></ng-pluralize>
    	</span>
    	<button id="clear-completed" ng-click="clearCompletedTodos()" ng-show="completedCount()">Clear completed ({{completedCount()}})</button>
    	</footer>

	Add to the bottom of the scripts section at the bottom:
    			
    	<script src="js/controllers/todoCtrl.js"></script>

2.  Now lets create the file js/controllers/todoCtrl.js and put the following code inside of the file:
    
    	var app = angular.module('todomvc',["ngResource"]);
    
    	app.factory('todoFactory', function($resource) {
        	var apiRoot='//' + window.location.host + '/_ah/api/todoapi/v1/todo/:id';
        	return $resource(apiRoot,
            	{'update': {method: 'PUT'}},
            	{'query':  {method:'GET', isArray:true,
                	transformResponse: function(data, headers){
                    	return JSON.parse(data)['items'];
                	}
            	}}
        	);
    	});
    
    	app.controller('TodoCtrl',function($scope,todoFactory){
      		$scope.todos = [];
      		$scope.newTodo = '';
      		$scope.remaining = function() {
        		var count = 0;
        		angular.forEach($scope.todos, function(todo) {
          			count += todo.done ? 0 : 1;
        		});
        		return count;
      		};
      		$scope.completedCount = function(){
          		return $scope.todos.length - $scope.remaining();
      		}
      		$scope.allChecked = false;
    
      		$scope.loadTodos = function() {
            	$scope.todos = todoFactory.query();
      		}
    
      		$scope.change = function(item){
          		item.$save();
      		}
      		$scope.removeTodo = function(item){
          		todoFactory.delete({ id: item.id });
          		$scope.todos=_.filter($scope.todos,function(it){
             		return it != item;
          		});
      		}

      		$scope.addTodo = function() {
        		var newTodo = new todoFactory({text:$scope.newTodo, done:false});
        		newTodo.$save();
    
        		$scope.todos.push(newTodo);
        		$scope.newTodo = '';
      		};


        	$scope.doneEditing = function (todo) {
            	$scope.editedTodo = null;
            	todo.text = todo.text.trim();
            	$scope.change(todo);
            	if (!todo.text) {
                    $scope.removeTodo(todo);
            	}
        	};


    		$scope.editTodo = function (todo) {
        		$scope.editedTodo = todo;
        		// Clone the original todo to restore it on demand.
        		$scope.originalTodo = angular.extend({}, todo);
    		};

    		$scope.markAll = function (completed) {
        		$scope.todos.forEach(function (todo) {
                	todo.done = !completed;
                	$scope.change(todo);
        		});
    		};

        	$scope.clearCompletedTodos = function () {
            	$scope.todos.forEach(function(todo){
               	console.log(todo);
               	if (todo.done){
                    todoFactory.delete({ id: todo.id });
                    $scope.todos=_.filter($scope.todos,function(it){
                        return it != todo;
                    });
               }
            });
        };
    
        $scope.loadTodos();
    
    	});

Here the "todomvc" must have the same name as used in the index.html file in the html section ng-app="todomvc".
The ngResource will help us make a rest service.  To read more about this https://docs.angularjs.org/api/ngResource/service/$resource

    var app = angular.module('todomvc',["ngResource"]);

Here we are setting up the factory that will transmit the data to and from the server.  We first need to point the rest service in the right place

    apiRoot='//' + window.location.host + '/_ah/api/todoapi/v1/todo/:id';

Then we create a couple custom calls to use, update and query.  



    app.factory('todoFactory', function($resource) {
        var apiRoot='//' + window.location.host + '/_ah/api/todoapi/v1/todo/:id';
        return $resource(apiRoot,
            {'update': {method: 'PUT'}},
            {'query':  {method:'GET', isArray:true,
                transformResponse: function(data, headers){
                    console.log(data);
                    return JSON.parse(data)['items'];
                }
            }}
    
        );
    });
Here we set up the controller and include the todoFactory.

    app.controller('TodoCtrl',function($scope,todoFactory){

This sets up the array that will hold the todos from the server.

      $scope.todos = [];

This sets up the variable to hold a temporary todo when we create a new todo.

      $scope.newTodo = '';

This function loops through the todos and counts how many of todos are done.

      $scope.remaining = function() {
        var count = 0;
        angular.forEach($scope.todos, function(todo) {
          count += todo.done ? 0 : 1;
        });
        return count;
      };

This function returns the number of todos that are complete.

      $scope.completedCount = function(){
          return $scope.todos.length - $scope.remaining();
      }

This is used as the model for toggle-all. 

    $scope.allChecked = false;

 
This function calls the todoFactory and gets a list of todos from the server. 

      $scope.loadTodos = function() {
            $scope.todos = todoFactory.query();
      }

This function is passed a todo and saves that todo to the server.

      $scope.change = function(item){
          item.$save();
      }

This function is passed a todo and deletes that todo on the server and removes the todo from the local list. 

      $scope.removeTodo = function(item){
          todoFactory.delete({ id: item.id });
          $scope.todos=_.filter($scope.todos,function(it){
             return it != item;
          });
      }

This function is used to create a new todo using the todoFactory and saving that todo to the server as well as adding the todo to the local list. 

      $scope.addTodo = function() {
        var newTodo = new todoFactory({text:$scope.newTodo, done:false});
        newTodo.$save();
    
        $scope.todos.push(newTodo);
        $scope.newTodo = '';
      };

This function is called when the user has finished editing a todo. We clear out the editedTodo, trim the text and then save the content by calling change with the todo as a parameter.

    $scope.doneEditing = function (todo) {
        $scope.editedTodo = null;
        todo.text = todo.text.trim();
        $scope.change(todo);
        if (!todo.text) {
                $scope.removeTodo(todo);
        }
    };

This is called when a user edits a todo.   First we put the todo in the editedTodo holder and save the original in the originalTodo.  We will use this more in the next version of the code.

    $scope.editTodo = function (todo) {
        $scope.editedTodo = todo;
        // Clone the original todo to restore it on demand.
        $scope.originalTodo = angular.extend({}, todo);
    };

This function marks all todos as done or not done depending on how the mark all is toggled.  

    $scope.markAll = function (completed) {
        $scope.todos.forEach(function (todo) {
                todo.done = !completed;

                $scope.change(todo);
        });
    };

This function loops through all the todos and deletes the ones that are done.  

    $scope.clearCompletedTodos = function () {
        $scope.todos.forEach(function(todo){
           if (todo.done){
                todoFactory.delete({ id: todo.id });
                $scope.todos=_.filter($scope.todos,function(it){
                    return it != todo;
                });
           }
        });
    };




3.   Finish hooking up the index file.  
  a.  In the bp_content/themes/default/handlers/handlers.py file add


    	class TestAngular(BaseHandler):
        def get(self,**kwargs):
            params = {
            }
            return self.render_template('index.html', **params)

  b.  in the bp_content/themes/default/routes/__init__.py file add the following route

    	RedirectRoute('/', handlers.TestAngular, name='home', strict_slash=True)

  c.  in the bp_includes/routes.py file comment out the home route
    	#RedirectRoute('/', handlers.HomeRequestHandler, name='home', strict_slash=True)


Voila!  We are done, and have a great example of google endpoints being used to supply data to an angular front end.




