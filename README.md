# Todo app using Flask, Postgres, SQLAlchemy and Python

This is a not so simple todo application that implements CRUD functionality. You can create a list of Todo items, manage the list of items and delete them when you feel satisfied with the items on the list and no longer have a need for them.

## Basic analysis of this app

Flask Todo app with two models - TodoList and Todo. Uses SQLite in-memory database. Key
  features:

  Models:
  - TodoList: Has id, name, and todos relationship (app.py:14-26)
  - Todo: Has id, description, completed status, and todolist_id foreign key
  (app.py:28-41)

  Routes:
  - POST /todos/<todolist_id>: Create new todo (app.py:52-73)
  - POST /todos: Create new todo list (app.py:76-96)
  - PATCH /todos/<list_id>/<todo_id>: Update todo completion status (app.py:99-119)
  - PUT /todos/<list_id>: Mark all todos in list as complete (app.py:122-141)
  - DELETE /todos/<list_id>/<todo_id>: Delete specific todo (app.py:144-170)
  - DELETE /todos/<list_id>: Delete entire todo list (app.py:173-193)
  - GET /todos/<list_id>: Display todo list with template (app.py:196-227)
  - GET /: Redirect to first todo list or welcome page (app.py:230-232)

  Special Features:
  - Welcome page with dummy starter tasks (app.py:204-227)
  - Tracks deleted starter tasks in memory (app.py:46-49)
  - Database tables created automatically on startup (app.py:43-44)


## Usage

1. This app has been modified to use with DA projects. The `app.py` file has a statement with  SQLALCHEMY_DATABASE_URI which you provide a connection string. The default an in-memory database. You can setup SQL Alchemy if you like to a postgres db with the right connection string.

2. Create a venv and activate it. The use pip to install the dependencies in the requirements.txt file.

3. Run the app: python app.py.

This has been tested with python 3.11.12.

And that should do it. Have fun with the app.

## Note from DA Python template

# Docker Dev Env for Python Flask

# Running tests

This command builds a docker image with the code of this repository and runs the repository's tests

```sh
./build_docker.sh my_app
docker run -t my_app ./run_tests.sh
```


```
# Running a specific test

This example runs a single test in the class TodoTestCase, with the name "test_home"

```sh
./build_docker.sh my_app
docker run -t my_app ./run_tests.sh TodoTestCase.test_home
```

# Running a flask dev server

Run this command to enable hot reloading via docker.

```sh
./build_docker.sh my_app
docker run --network=host -v .:/app -t my_app flask init_db
docker run --network=host -v .:/app -t my_app flask run
```
