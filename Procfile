web: gunicorn project.core.asgi:application -w $GUNICORN_WORKERS -b unix:/app/mb-mms.sock -k uvicorn.workers.UvicornWorker -e SIMPLE_SETTINGS=$SIMPLE_SETTINGS
worker: celery --workdir=src -A project.core.celery worker --concurrency=$CELERY_WORKER_CONCURRENCY -l info -Ofair --without-mingle --without-gossip --without-heartbeat
beat: celery --workdir=src -A project.core.celery beat -l info -S django
release: SIMPLE_SETTINGS=$SIMPLE_SETTINGS python manage.py migrate --no-input
