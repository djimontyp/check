COMPOSE = docker-compose -f docker-compose.yml
MANAGE_PY = python3 app/manage.py

RESET := $(shell tput -Txterm sgr0)
BLUE := $(shell tput -Txterm setaf 6)
TARGET_COLOR := $(BLUE)

include .docker.env
export

.PHONY: no_targets__ help
	no_targets__:

.DEFAULT_GOAL := help

help:
	@grep -E '^[a-zA-Z_0-9%-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "${TARGET_COLOR}%-30s${RESET} %s\n", $$1, $$2}'


run:  	      ## Run project
	$(MANAGE_PY) wait_for_db && \
	$(MANAGE_PY) migrate --no-input && \
	$(MANAGE_PY) collectstatic --no-input && \
	$(MANAGE_PY) runserver localhost:8000

docker-run:  	      ## Run project in docker
	$(COMPOSE) up

mm-m:            ## Migrate migrations in app container
	$(MANAGE_PY) makemigrations && \
	$(MANAGE_PY) migrate

fixtures: 		  ## Load fixtures
	$(MANAGE_PY) loaddata printers.json

build: 	  ## Build project
	$(COMPOSE) build