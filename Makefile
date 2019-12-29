SHELL := /bin/bash

ALLURE_DIR ?= .allure
COVERAGE_DIR ?= .coverage-html

export ARGS

test: coverage check-coverage

static:
	pre-commit run --all-files

coverage:
	coverage run --concurrency=eventlet --source users --branch -m pytest --alluredir=$(ALLURE_DIR) tests$(ARGS)
	coverage html -d $(COVERAGE_DIR)

check-coverage:
	coverage report -m --fail-under 100  --omit=users/dependencies/sendgrid/provider.py

run:
	nameko run --config config.yml users.service:UsersService

build-image:
	docker build -t calumwebb/users-service:$(TAG) .;

push-image:
	docker push calumwebb/users-service:$(TAG)