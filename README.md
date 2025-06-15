# Todo app using Flask, Postgres, SQLAlchemy and Python

This is a not so simple todo application that implements CRUD functionality. You can create a list of Todo items, manage the list of items and delete them when you feel satisfied with the items on the list and no longer have a need for them.

## Usage

1. Go to line 8 of the `app.py` file and modify the SQLALCHEMY_DATABASE_URI app configuration to match the database connection settings you have set up in your machine.
   Follow this format:
   ![Format for setting the SQLALCHEMY_DATABASE_URI app configuration](https://video.udacity-data.com/topher/2019/August/5d4df44e_database-connection-uri-parts/database-connection-uri-parts.png)

2. Install Postgres and get its server running  
   On a Unix machine, to start the server, you can use the following command:

   ```bash
   >>$ sudo service postgresql start
   ```

   On a Windows machine, to start the server, you can use the following command:

   ```bash
   >>$ pg_ctl.exe start -D 'C:/Program Files/PostgreSQL/<version number>/data'
   ```

3. Now, on your terminal, `cd` to the project directory and run:

   ```bash
   >>$ source .bash
   ```

And that should do it. Have fun with the app.

## From DA Python template

# Docker Dev Env for Python Flask

# Running tests

This command builds a docker image with the code of this repository and runs the repository's tests

```sh
./build_docker.sh my_app
docker run -t my_app ./run_tests.sh
```

```
[+] Building 0.1s (10/10) FINISHED                                                            docker:default
 => [internal] load build definition from Dockerfile                                                    0.0s
 => => transferring dockerfile: 248B                                                                    0.0s
 => [internal] load metadata for docker.io/library/python:3.13.2-alpine3.21@sha256:323a717dc4a010fee21  0.0s
 => [internal] load .dockerignore                                                                       0.0s
 => => transferring context: 94B                                                                        0.0s
 => [1/5] FROM docker.io/library/python:3.13.2-alpine3.21@sha256:323a717dc4a010fee21e3f1aac738ee10bb48  0.0s
 => [internal] load build context                                                                       0.0s
 => => transferring context: 253B                                                                       0.0s
 => CACHED [2/5] WORKDIR /app                                                                           0.0s
 => CACHED [3/5] COPY requirements.txt .                                                                0.0s
 => CACHED [4/5] RUN pip install --no-cache-dir -r requirements.txt                                     0.0s
 => CACHED [5/5] COPY . .                                                                               0.0s
 => exporting to image                                                                                  0.0s
 => => exporting layers                                                                                 0.0s
 => => writing image sha256:4e6c980fbf83b2131359af3d3730e61c89ae7dc85e23c151114b0d9d4a749158            0.0s
 => => naming to docker.io/library/my_app                                                               0.0s

....
----------------------------------------------------------------------
Ran 4 tests in 0.069s

OK
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
