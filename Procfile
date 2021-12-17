web: gunicorn project.core.asgi:application -w $GUNICORN_WORKERS -k uvicorn.workers.UvicornWorker -e SIMPLE_SETTINGS=$SIMPLE_SETTINGS
