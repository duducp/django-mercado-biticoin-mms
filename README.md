# Médias Móveis Simples

Main dependencies:
- Django
- Django Ninja

Compatibility:
- Python 3.9.5
- Django 3.2.3

## Navigation
- [First steps](#first_steps)
- [Development mode](#development_mode)
- [Deploying in production](#deploying_prod)
- [Docker](#docker)
- [Create new app](#create_app)
- [Application code versioning](#app_versioning)
- [Migrate and migration](#migrate_migration)
- [Logs](#logs)
- [Correlation ID](#correlation_id)

<a id="first_steps"></a>
### First steps
First, you must configure the virtual environment:
```shell script
python -m venv venv
```

After that activate virtualenv:
```shell script
source venv/bin/activate
```

Run the command to install the development dependencies:
```shell script
make dependencies
```

Last and most important set the environment variables by cloning the
**.env-sample** file to **.env-development**

<a id="development_mode"></a>
### Development mode
The development mode by default uses Postgres as a database.

Run the command to create the tables in the database:
```shell script
make migrate
```

To access the admin it is necessary to create the superuser. This can be done
with the following command:
```shell script
make superuser
```

To see which routes exist in the application, execute the command:
```shell script
make urls
```

Now just run the command below to run the application:
```shell script
make run
```

After running the command above, you can access the documentation and the administrative panel:
```
http://localhost:8000/admin
http://localhost:8000/ping
http://localhost:8000/v1/docs
```

<a id="deploying_prod"></a>
### Deploying application in production
To deploy to production the following environment variables must be defined:
```shell script
export SIMPLE_SETTINGS=core.settings.production
export GUNICORN_WORKERS=1
export SECRET_KEY="your_key_here"
export DATABASE_URL="sqlite:///db.sqlite3"
export DATABASE_READ_URL="sqlite:///db.sqlite3"
```

Optionals:
```shell script
export ALLOWED_HOSTS="*;"
```

If this is your first time running the application on a production database,
you should apply the migration and create the superuser.

<a id="docker"></a>
### Docker
This application makes use of Docker to facilitate during development in order to raise external dependencies (Postgres and Redis).

Before executing the commands, make sure you have the docker installed on your device.

See the commands available in the Makefile:
- make **docker-app-up**: Create docker containers from Rest application.
- make **docker-app-down**: Remove docker containers from Rest application.
- make **docker-app-logs**: View logs in the Rest application of the docker container.
- make **docker-app-migrate**: Apply the database migration in the Rest application of the docker container.
- make **docker-app-superuser**: Create superuser in docker container Rest application.
- make **docker-dependencies-up**: Creates the docker containers with the application dependencies.
- make **docker-dependencies-down**: Removes the docker containers with the application dependencies.
- make **docker-dependencies-downclear**: Removes the docker containers and volumes with the application dependencies.

<a id="create_app"></a>
### Create new app
All new apps are created in the _src/apps_ directory and to create a new
app you can run the following command:
```shell script
make app name=clients
```

Note that the _name_ parameter has been passed. It is used to inform the name
of the application.

<a id="app_versioning"></a>
### Application code versioning
A good practice it is always good to create a _changelog_ file in each
completed task in order to keep a history of the change. For that we have some
commands:

- changelog-feature: signifying a new feature
- changelog-bugfix: signifying a bug fix
- changelog-doc: signifying a documentation improvement
- changelog-removal: signifying a deprecation or removal of public API

Each of these commands expects the **filename** and **message** parameter. You
can use them as follows:

```shell script
make changelog-feature filename="create-crud-client" message="Adds CRUD for clients management"
```

When a story is finished it is time to create a new version for the
application. All _changelog_ files in existence will be converted to a single
message that will be available in the _CHANGELOG_ file.

There are three commands that we use to close the version. Are they:

- release-patch: create patch release eg 0.0.1
- release-minor: create minor release eg 0.1.0
- release-major: create major release eg 1.0.0

You can use them as follows:
```shell script
make release-patch
```

After running the specific command, two new commits will be created, one
referring to the generation of the changelog file and the other referring to
the generation of the new version of the application. In addition to these new
commits, a specific tag for the application version is also generated.

Finally, you can submit all changes to your git repository with the `make push`
command.

<a id="migrate_migration"></a>
### Migrate and migration
If you've just set up your model, it's time to create the schema to be applied
to the database in the future. Notice that in your app there is a folder with
the name of **migrations**, this is where the schematics of your model will
stay.

To create the schema we need to execute the following command:
```shell script
make migration
```

You can also create a blank layout, which in turn will not be related to any
model at first:
```shell script
make migration-empty app=clients
```

Note that the _app_ parameter has been passed. It is used to tell which app the
schema should be created in.

Now we need to apply this schema to the database and for that we execute the
following command:
```shell script
make migrate
```

<a id="logs"></a>
### Logs
The application logs are more powerful and less painful with the help of
**structlog** which is intermediated by `structlog`. All logs made are
converted to JSON, thus facilitating their search, since they are keyed.

For you to use them just follow the code below:
```python
import structlog
logger = structlog.get_logger(__name__)

logger.info("User logged in", user="test-user")
```

<a id="correlation_id"></a>
### Correlation ID
This application uses [django-cid](https://pypi.org/project/django-cid/)
to do the management.

The correlation is injected into the logs and returned in the header of each
request. The user can send it in the request header (X-Correlation-ID) or if it
is not found, the application will automatically generate it.
