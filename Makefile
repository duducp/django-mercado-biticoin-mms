PROJECT_PATH=./src/project
FILE_ENV=.env-development
BRANCH_NAME=$(shell git rev-parse --abbrev-ref HEAD)

export PYTHONPATH=src

ifneq (,$(wildcard $(FILE_ENV)))
    include $(FILE_ENV)
    export
endif

define SET_ENV_DOCKER_APP
	DOCKER_BUILDKIT=1 \
	DATABASE_URL=postgres://postgres:postgres@postgres:5432/postgres \
	DATABASE_READ_URL=postgres://postgres:postgres@postgres:5432/postgres \
	CELERY_BROKER_URL=redis://redis:6379/1 \
	REDIS_URL=redis://redis:6379/1 \
	REDIS_URL_LOCK=redis://redis:6379/1
endef

help:  ## This help
	@echo 'To see the available Django commands, run the following command at the root of the project "python src/manage.py".'
	@echo "For more information read the project Readme."
	@echo
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

clean: ## Clean local environment
	@find . -name "*.pyc" | xargs rm -rf
	@find . -name "*.pyo" | xargs rm -rf
	@find . -name "__pycache__" -type d | xargs rm -rf
	@rm -f .coverage
	@rm -rf htmlcov/
	@rm -f coverage.xml
	@rm -f *.log

dependencies: ## Install development dependencies
	pip install -U -r requirements/dev.txt
	pre-commit install

pre-commit: ## Configure pre-commit to keep the code organized when committing and pushing
	pre-commit install

collectstatic: ## Creates static files for admin
	python src/manage.py collectstatic --noinput #--clear

app:  ## Creates a new django application Ex.: make app name=products
	cd $(PROJECT_PATH) && python ../manage.py startapp --template=../../.template/app_name.zip -e py -e md $(name)
	@echo 'Application created in "$(PROJECT_PATH)/$(name)"'
	@echo 'Read the README for more details: $(PROJECT_PATH)/$(name)/Readme.md'

run: collectstatic  ## Run the django project
	-$(MAKE) docker-dependencies-up
	gunicorn -b 0.0.0.0:8000 -t 300 project.core.asgi:application -w $(GUNICORN_WORKERS) -k uvicorn.workers.UvicornWorker --log-level debug --reload

superuser: ## Creates superuser for admin
	python src/manage.py createsuperuser

migrate: migration  ## Apply migrations to the database
	-$(MAKE) docker-dependencies-up
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

lint: ## Performs the project lint to detect possible errors
	isort .
	sort-requirements requirements/base.txt
	sort-requirements requirements/prod.txt
	sort-requirements requirements/dev.txt
	sort-requirements requirements/test.txt
	flake8 --show-source .
	pycodestyle --show-source .

safety-check: ## Checks libraries safety
	safety check -r requirements/base.txt
	safety check -r requirements/prod.txt
	safety check -r requirements/dev.txt
	safety check -r requirements/test.txt


docker-up-all: ## Start all docker container from application
	@echo "Starting all containers docker..."
	-$(MAKE) docker-dependencies-up
	-$(MAKE) docker-app-up
	-$(MAKE) docker-celery-up
	@echo
	-$(shell) docker ps

docker-down-all: ## Removes all docker container from application
	@echo "Removing all containers docker..."
	-$(MAKE) docker-app-down
	-$(MAKE) docker-celery-down
	-$(MAKE) docker-dependencies-down
	@echo
	-$(shell) docker ps

docker-restart-all: ## Restart all docker container from application
	@echo "Restarting all containers docker..."
	-$(MAKE) docker-app-restart
	-$(MAKE) docker-celery-restart
	-$(MAKE) docker-dependencies-restart
	@echo
	-$(shell) docker ps

docker-app-up: ## Create docker containers from Rest application
	@echo "Starting application with docker..."
	-$(MAKE) docker-dependencies-up
	$(SET_ENV_DOCKER_APP) docker-compose -f docker-compose-app.yml up -d --build
	@echo "Application running on http://localhost:8000"

docker-app-down: ## Remove docker containers from Rest application
	@echo "Removing docker containers from application..."
	-$(SET_ENV_DOCKER_APP) docker-compose -f docker-compose-app.yml down
	@echo
	@echo "To also remove dependency containers you must run the command 'docker-dependencies-down'"

docker-app-logs: ## View logs in the Rest application of the docker container
	$(SET_ENV_DOCKER_APP) docker-compose -f docker-compose-app.yml logs -f

docker-app-restart: ## Restart the docker container from Rest application
	@echo "Restarting docker containers Rest application..."
	$(SET_ENV_DOCKER_APP) docker-compose -f docker-compose-app.yml restart

docker-app-migrate: ## Apply the database migration in the Rest application of the docker container
	$(SET_ENV_DOCKER_APP) docker-compose -f docker-compose-app.yml exec web python manage.py migrate --noinput

docker-app-superuser: ## Create superuser in docker container Rest application
	$(SET_ENV_DOCKER_APP) docker-compose -f docker-compose-app.yml exec web python manage.py createsuperuser

docker-celery-up: ## Create docker containers from Celery
	@echo "Starting Celery worker with docker..."
	-$(MAKE) docker-dependencies-up
	$(SET_ENV_DOCKER_APP) docker-compose -f docker-compose-celery.yml up -d --build

docker-celery-down: ## Remove docker containers from Celery
	@echo "Removing docker containers from Celery..."
	-$(SET_ENV_DOCKER_APP) docker-compose -f docker-compose-celery.yml down
	@echo
	@echo "To also remove dependency containers you must run the command 'docker-dependencies-down'"

docker-celery-logs: ## View logs in the Celery of the docker container
	$(SET_ENV_DOCKER_APP) docker-compose -f docker-compose-celery.yml logs -f

docker-celery-restart: ## Restart the docker container from Celery
	@echo "Restarting docker containers from Celery..."
	$(SET_ENV_DOCKER_APP) docker-compose -f docker-compose-celery.yml restart

docker-dependencies-up: ## Creates the docker containers with the application dependencies
	@echo "Starting docker container with application dependencies..."
	docker-compose -f docker-compose-dependencies.yml up -d --build

docker-dependencies-down: ## Removes the docker containers with the application dependencies
	@echo "Removing docker containers with application dependencies..."
	-docker-compose -f docker-compose-dependencies.yml down

docker-dependencies-downclear: ## Removes the docker containers and volumes with the application dependencies
	@echo "Removing containers and volumes docker with application dependencies..."
	-docker-compose -f docker-compose-dependencies.yml down -v

docker-dependencies-restart: ## Restart the docker container from dependencies
	@echo "Restarting docker containers application dependencies..."
	docker-compose -f docker-compose-dependencies.yml restart


celery-run:  ## Start Celery worker
	celery --workdir=src -A project.core.celery worker --concurrency=1 -l debug -Ofair --without-mingle --without-gossip --without-heartbeat

celery-queue-run:  ## Start Celery worker queue Ex.: make celery-queue-run queue=
	celery --workdir=src -A project.core.celery worker --concurrency=1 -l debug -Ofair --without-mingle --without-gossip --without-heartbeat -Q $(queue)

celery-beat-run:  ## Start Celery Beat
	celery --workdir=src -A project.core.celery beat -l info -S django


test: clean ## Run the application unit tests
	pytest -x

test-matching: clean ## Run the match tests
	pytest -x -k $(q) --pdb

test-coverage: clean ## Performs tests with coverage
	pytest -x --cov=src/ --cov-report=term-missing --cov-report=xml

test-coverage-html: clean ## Run tests with coverage and generate html report
	pytest -x --cov=src/ --cov-report=html:htmlcov

test-coverage-html-server: test-coverage-html ## Run tests with coverage and open the server to view coverage
	cd htmlcov && python -m http.server 8001 --bind 0.0.0.0


changelog-improvement: ## Create changelog file for code improvements
	@echo $(message) > changelog/${BRANCH_NAME}.improvement

changelog-feature: ## Creates changelog file for new feature
	@echo $(message) > changelog/${BRANCH_NAME}.feature

changelog-bugfix: ## Creates changelog file for bug fix
	@echo $(message) > changelog/${BRANCH_NAME}.bugfix

changelog-doc: ## Creates changelog file for documentation improvement
	@echo $(message) > changelog/${BRANCH_NAME}.doc

changelog-removal: ## Creates changelog file for deprecation or removal of public API
	@echo $(message) > changelog/${BRANCH_NAME}.removal

changelog-misc: ## Creates a changelog file where the changes are not of interest to the end user
	@echo $(message) > changelog/${BRANCH_NAME}.misc

release-patch: ## Creates patch release (0.0.1)
	bumpversion patch --dry-run --no-tag --no-commit --list | grep new_version= | sed -e 's/new_version=//' | xargs -n 1 towncrier --yes --version
	git commit -am 'Update CHANGELOG'
	bumpversion patch
	@echo 'New commit and new tag created.'
	@echo 'Run "make push" to send them to github.'

release-minor: ## Creates minor release (0.1.0)
	bumpversion minor --dry-run --no-tag --no-commit --list | grep new_version= | sed -e 's/new_version=//' | xargs -n 1 towncrier --yes --version
	git commit -am 'Update CHANGELOG'
	bumpversion minor
	@echo 'New commit and new tag created.'
	@echo 'Run "make push" to send them to github.'

release-major: ## Creates major release (1.0.0)
	bumpversion major --dry-run --no-tag --no-commit --list | grep new_version= | sed -e 's/new_version=//' | xargs -n 1 towncrier --yes --version
	git commit -am 'Update CHANGELOG'
	bumpversion major
	@echo 'New commit and new tag created.'
	@echo 'Run "make push" to send them to github.'

push: ## Push commits and tags to the remote Git repository
	git push && git push --tags

.PHONY: run shell urls info app
