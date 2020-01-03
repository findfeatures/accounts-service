SHELL := /bin/bash

ALLURE_DIR ?= .allure
COVERAGE_DIR ?= .coverage-html

export ARGS

test: coverage check-coverage

static:
	pre-commit run --all-files

coverage:
	coverage run --concurrency=eventlet --source accounts --branch -m pytest --alluredir=$(ALLURE_DIR) tests$(ARGS)
	coverage html -d $(COVERAGE_DIR)

check-coverage:
	coverage report -m --fail-under 100  --omit=accounts/dependencies/send_grid/provider.py

run:
	nameko run --config config.yml accounts.service:AccountsService

build-image:
	docker build -t calumwebb/accounts-service:$(TAG) .;

push-image:
	docker push calumwebb/accounts-service:$(TAG)