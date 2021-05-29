# Médias Móveis Simples

Main dependencies:
- Django
- Django Ninja

Compatibility:
- Python 3.9.5
- Django 3.2.3

## Navigation
- [Development mode](#development_mode)
- [Deploying in production](#deploying_prod)

<a id="development_mode"></a>
### Development mode

The development mode by default uses Sqlite as a database.

First, you must configure the virtual environment:
```shell script
python -m venv venv
```

After that activate virtualenv:
```shell script
source venv/bin/activate
```

Set the environment variables by cloning the **.env-sample** file to **.env-development**

Run the command to install the development dependencies:
```shell script
make dependencies
```

Now, run the command to create the tables in the database:
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
http://localhost:8000/v1/docs
```

<a id="deploying_prod"></a>
### Deploying application in production

To deploy to production the following environment variables must be defined:
```shell script
export SIMPLE_SETTINGS=core.settings.production
export GUNICORN_WORKERS=1
export SECRET_KEY="your_key_here"
```

Optionals:
```shell script
export ALLOWED_HOSTS="*;"
```
