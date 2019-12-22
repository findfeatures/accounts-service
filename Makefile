SHELL := /bin/bash

SHELL := /bin/bash

ALLURE_DIR ?= .allure
COVERAGE_DIR ?= .coverage-html

export ARGS

.PHONY: help
.DEFAULT: help
help: Makefile
	@echo "make <command>"
	@sed -n 's/^##//p' $<

.PHONY: test
##  test              Run full set of tests.
test: coverage check-coverage

.PHONY: static
##  static            Run static analysis.
static:
	pre-commit run --all-files

.PHONY: coverage
##  coverage          Run unit tests with coverage report.
coverage:
	coverage run --concurrency=eventlet --source users --branch -m pytest --alluredir=$(ALLURE_DIR) tests$(ARGS)
	coverage html -d $(COVERAGE_DIR)

.PHONY: check-coverage
##  check-coverage    Print existing coverage report (fail under 100%).
check-coverage:
	coverage report -m --fail-under 100

.PHONY: run
##  run               Run API service.
run:
	nameko run --config config.yml users.service
