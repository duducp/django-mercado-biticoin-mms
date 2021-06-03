web: gunicorn project.core.asgi:application -w $GUNICORN_WORKERS -b unix:/app/mb-mms.sock -k uvicorn.workers.UvicornWorker -e SIMPLE_SETTINGS=$SIMPLE_SETTINGS
release: SIMPLE_SETTINGS=$SIMPLE_SETTINGS python manage.py migrate --no-input
