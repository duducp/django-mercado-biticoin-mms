PROJECT_PATH=./src/apps
PROJECT_SETTINGS=core.settings.development
WORKERS_GUNICORN=1
FILE_ENV=.env-development

export PYTHONPATH=src
export SIMPLE_SETTINGS=$(PROJECT_SETTINGS)
export DJANGO_SETTINGS_MODULE=$(PROJECT_SETTINGS)
export GUNICORN_WORKERS=$(WORKERS_GUNICORN)

ifneq (,$(wildcard $(FILE_ENV)))
    include $(FILE_ENV)
    export
endif

help:  ## This help
	@echo "To see the available Django commands, run the following command at the root of the project: python src/manage.py"
	@echo "For more information read the project Readme."
	@echo
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

dependencies: ## Install development dependencies
	pip install -U -r requirements/dev.txt

collectstatic: ## Creates static files for admin
	python src/manage.py collectstatic --noinput #--clear

app:  ## Creates a new django application Ex.: make app name=products
	cd $(PROJECT_PATH) && python ../../manage.py startapp $(name)
	@echo 'Application created in "$(PROJECT_PATH)/$(name)"'

run: collectstatic  ## Run the django project
	gunicorn -b 0.0.0.0:8000 -t 300 core.asgi:application -w $(GUNICORN_WORKERS) -k uvicorn.workers.UvicornWorker --log-level debug --reload

superuser: ## Creates superuser for admin
	python src/manage.py createsuperuser

migrate:  ## Apply migrations to the database
	python src/manage.py migrate

migration:  ## Creates migration file according to the models
	python src/manage.py makemigrations

migration-empty:  ## Creates blank migration file
	python src/manage.py makemigrations --empty $(app)

migration-detect:  ## Detect missing migrations
	python src/manage.py makemigrations --dry-run --noinput | grep 'No changes detected' -q || (echo 'Missing migration detected!' && exit 1)

dumpdata:  ## Removes all data registered in the database
	@echo "By continuing all data in your database will be deleted."
	@echo "Press ENTER to continue..."
	@read y
	python src/manage.py dumpdata

urls:  ## View available routes in the app
	python src/manage.py show_urls

shell:  ## Opens the project shell
	python src/manage.py shell_plus --ipython  # shell -i ipython

.PHONY: run shell urls info app
