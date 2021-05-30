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
- [Create new app](#create_app)
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

<a id="create_app"></a>
### Create new app
All new apps are created in the _src/apps_ directory and to create a new
app you can run the following command:
```shell script
make app name=clients
```

Note that the _name_ parameter has been passed. It is used to inform the name
of the application.

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
