var app = angular.module('todomvc',["ngResource"]);

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





