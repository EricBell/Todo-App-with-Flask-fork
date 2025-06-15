from flask import Flask, jsonify, render_template, request, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import sys

app = Flask(__name__)
# Using SQLite in-memory database instead of PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class TodoList(db.Model):
    # Table name
    __tablename__ = 'todolist'
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    todos = db.relationship('Todo', backref='todolist',
                            lazy=True, cascade='all, delete', passive_deletes=True)

    # Object Representation
    def __repr__(self):
        return f"\n<TodoList id:{self.id} name:{self.name}>"


class Todo(db.Model):
    # Table name
    __tablename__ = 'todo'
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(), nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)
    todolist_id = db.Column(db.Integer, db.ForeignKey(
        "todolist.id", ondelete="CASCADE"), nullable=False)

    # Object Representation
    def __repr__(self):
        return f"\n<Todo id:{self.id}, description:{self.description} completed:{self.completed}>"

# Create tables for in-memory database (migrations not needed for in-memory)
with app.app_context():
    db.create_all()

def get_deleted_tasks():
    if not hasattr(app, 'deleted_starter_tasks'):
        app.deleted_starter_tasks = set()
    return app.deleted_starter_tasks


@app.route('/todos/<todolist_id>', methods=['POST'])
def create_todo(todolist_id):
    error = False
    body = {}
    try:
        description = request.get_json()['description']
        todolist_id = request.get_json()['todolist_id']
        todo = Todo(description=description, todolist_id=todolist_id)
        db.session.add(todo)
        db.session.commit()
        body['id'] = todo.id
        body['description'] = todo.description
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()

    if error:
        abort(400)
    else:
        return jsonify(body)


@app.route('/todos', methods=['POST'])
def create_list():
    error = False
    body = {}
    try:
        name = request.get_json()['name']
        list = TodoList(name=name)
        db.session.add(list)
        db.session.commit()
        body['id'] = list.id
        body['name'] = list.name
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()

    if error:
        abort(400)
    else:
        return jsonify(body)


@app.route('/todos/<list_id>/<todo_id>', methods=['PATCH'])
def update_todo(list_id, todo_id):
    print(list_id)
    error = False
    body = {}
    try:
        completed = request.get_json()['completed']
        todo = db.session.get(Todo, todo_id)
        todo.completed = completed
        db.session.commit()
        body['completed'] = todo.completed
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()

    if error:
        abort(400)
    else:
        return jsonify(body)


@app.route('/todos/<list_id>', methods=['PUT'])
def update_all(list_id):
    error = False
    body = {}
    try:
        todos = Todo.query.filter_by(todolist_id=list_id).all()
        for todo in todos:
            todo.completed = True
        db.session.commit()
        body['successful'] = not error
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()

    if error:
        abort(400)
    else:
        return jsonify(body)


@app.route('/todos/<list_id>/<todo_id>', methods=["DELETE"])
def delete_todo(list_id, todo_id):
    print(list_id)
    error = False
    body = {}
    
    if list_id == 'welcome':
        get_deleted_tasks().add(int(todo_id))
        body['successful'] = True
    else:
        try:
            # Alternative way
            # todo = Todo.query.get(todo_id)
            # db.session.delete(todo)
            Todo.query.filter_by(id=todo_id).delete()
            db.session.commit()
            body['successful'] = not error
        except:
            error = True
            db.session.rollback()
        finally:
            db.session.close()

    if error:
        abort(400)
    else:
        return jsonify(body)


@app.route('/todos/<list_id>', methods=["DELETE"])
def delete_list(list_id):
    error = False
    body = {}
    try:
        # Alternative way
        # todo = Todo.query.get(todo_id)
        # db.session.delete(todo)
        TodoList.query.filter_by(id=list_id).delete()
        db.session.commit()
        body['successful'] = not error
    except:
        error = True
        db.session.rollback()
    finally:
        db.session.close()

    if error:
        abort(400)
    else:
        return jsonify(body)


@app.route('/todos/<list_id>')
def get_todo_list(list_id):
    class DummyTodo:
        def __init__(self, id, description):
            self.id = id
            self.description = description
            self.completed = False
    
    dummyTodoList = [
        DummyTodo(1, 'Create a Todo'),
        DummyTodo(2, 'Accomplish the task'),
        DummyTodo(3, 'Remove the Todo'),
    ]

    dummyList = [
        {
            'id': 'welcome',
            'name': 'Starter Task',
        }
    ]

    name = dummyList[0]['name']
    newList_id = dummyList[0]['id']

    if not list_id == 'welcome':
        return render_template('index.html', data=Todo.query.filter_by(todolist_id=list_id).order_by('id').all(), list_id=list_id, list=TodoList.query.order_by('id').all(), name=db.session.get(TodoList, list_id).name)
    else:
        todos_to_show = []
        for todo in dummyTodoList:
            if todo.id not in get_deleted_tasks():
                todos_to_show.append(todo)
        return render_template('index.html', data=todos_to_show, list_id=newList_id, list=dummyList, name=name)


@app.route('/')
def index():
    return redirect(url_for('get_todo_list', list_id=TodoList.query.first().id if len(TodoList.query.all()) > 0 else 'welcome'))


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=3000)
