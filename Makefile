PROJECT_PATH=./src/apps
PROJECT_SETTINGS=core.settings.development
WORKERS_GUNICORN=1
FILE_ENV=.env-development

export PYTHONPATH=src

ifneq (,$(wildcard $(FILE_ENV)))
    include $(FILE_ENV)
    export
endif

define SET_ENV_DOCKER_APP
	SIMPLE_SETTINGS=$(SIMPLE_SETTINGS) \
	GUNICORN_WORKERS=$(GUNICORN_WORKERS) \
	SECRET_KEY=$(SECRET_KEY) \
	DJANGO_ALLOWED_HOSTS=$(DJANGO_ALLOWED_HOSTS) \
	DATABASE_URL=$(DATABASE_URL) \
	DATABASE_READ_URL=$(DATABASE_READ_URL)
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
	gunicorn -b 0.0.0.0:8000 -t 300 core.asgi:application -w $(GUNICORN_WORKERS) -k uvicorn.workers.UvicornWorker --log-level debug --reload

superuser: ## Creates superuser for admin
	python src/manage.py createsuperuser

migrate:  ## Apply migrations to the database
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


docker-app-up: ## Create docker containers from Rest application
	@echo "Starting application with docker..."
	-$(MAKE) docker-dependencies-up
	$(SET_ENV_DOCKER_APP) docker-compose -f docker-compose-app.yml up -d --build

docker-app-down: ## Remove docker containers from Rest application
	@echo "Removing docker containers from application..."
	-$(MAKE) docker-dependencies-down
	$(SET_ENV_DOCKER_APP) docker-compose -f docker-compose-app.yml down

docker-app-logs: ## View logs in the Rest application of the docker container
	$(SET_ENV_DOCKER_APP) docker-compose -f docker-compose-app.yml logs -f

docker-app-migrate: ## Apply the database migration in the Rest application of the docker container
	$(SET_ENV_DOCKER_APP) docker-compose -f docker-compose-app.yml exec web python manage.py migrate --noinput

docker-app-superuser: ## Create superuser in docker container Rest application
	$(SET_ENV_DOCKER_APP) docker-compose -f docker-compose-app.yml exec web python manage.py createsuperuser

docker-dependencies-up: ## Creates the docker containers with the application dependencies
	@echo "Starting docker container with application dependencies..."
	docker-compose -f docker-compose-dependencies.yml up -d --build

docker-dependencies-down: ## Removes the docker containers with the application dependencies
	@echo "Removing docker containers with application dependencies..."
	docker-compose -f docker-compose-dependencies.yml down

docker-dependencies-downclear: ## Removes the docker containers and volumes with the application dependencies
	@echo "Removing containers and volumes docker with application dependencies..."
	docker-compose -f docker-compose-dependencies.yml down -v


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


changelog-feature: ## Creates changelog file for new feature
	@echo $(message) > changelog/$(filename).feature

changelog-bugfix: ## Creates changelog file for bug fix
	@echo $(message) > changelog/$(filename).bugfix

changelog-doc: ## Creates changelog file for documentation improvement
	@echo $(message) > changelog/$(filename).doc

changelog-removal: ## Creates changelog file for deprecation or removal of public API
	@echo $(message) > changelog/$(filename).removal

changelog-misc: ## Creates a changelog file where the changes are not of interest to the end user
	@echo $(message) > changelog/$(filename).misc

release-patch: ## Creates patch release (0.0.1)
	bumpversion patch --dry-run --no-tag --no-commit --list | grep new_version= | sed -e 's/new_version=//' | xargs -n 1 towncrier --yes --version
	git commit -am 'Update CHANGELOG'
	bumpversion patch
	@echo 'To send the changes to the remote server run the make push command'

release-minor: ## Creates minor release (0.1.0)
	bumpversion minor --dry-run --no-tag --no-commit --list | grep new_version= | sed -e 's/new_version=//' | xargs -n 1 towncrier --yes --version
	git commit -am 'Update CHANGELOG'
	bumpversion minor
	@echo 'To send the changes to the remote server run the make push command'

release-major: ## Creates major release (1.0.0)
	bumpversion major --dry-run --no-tag --no-commit --list | grep new_version= | sed -e 's/new_version=//' | xargs -n 1 towncrier --yes --version
	git commit -am 'Update CHANGELOG'
	bumpversion major
	@echo 'To send the changes to the remote server run the make push command'

push: ## Push commits and tags to the remote Git repository
	git push && git push --tags

.PHONY: run shell urls info app
