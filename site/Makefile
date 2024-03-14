#* Variables
SHELL := /usr/bin/env bash
REPO_ROOT := $(shell git rev-parse --show-toplevel)

include .env

#* Setup
.PHONY: $(shell sed -n -e '/^$$/ { n ; /^[^ .\#][^ ]*:/ { s/:.*$$// ; p ; } ; }' $(MAKEFILE_LIST))
.DEFAULT_GOAL := help

help: ## list make commands
	@echo ${MAKEFILE_LIST}
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

#* Docker
# up: ## start prod docker-compose yml files
# 	sudo docker compose -f docker-compose.prod.yml up --build --remove-orphans

# upd: ## start prod docker-compose yml files
# 	sudo docker compose -f docker-compose.prod.yml up --build --remove-orphans -d

local: ## start site locally, uses override yml
	docker-compose -f docker-compose.yml up --build --remove-orphans

down: ## kills all docker-compose containers
	docker-compose down

logs: ## dc logs
	docker-compose logs -f

docker-kill: ## kill all docker containers
	for id in $$(docker ps --format "{{.ID}}"); do docker kill $$id; done

# deploy: cleanup deploy-prod ## clean, build, and rsync public files

# deploy-prod: ## build hugo app and rsync files
# 	@bash "${REPO_ROOT}/scripts/deploy.sh"

# getdb: ## retrieve database
# 	@bash "${REPO_ROOT}/scripts/getdb-prod.sh"

# copydevdb: ## copy local db instance
# 	@bash "${REPO_ROOT}/scripts/getdb-dev.sh"

#* Open
open: ## open browser to app and docs
	open http://worldcoin.willwrighteng.local:${APP_PORT}
	open http://worldcoin.willwrighteng.local:${BACKEND_PORT}/api/docs

# console: ## open aws console
# 	open https://s3.console.aws.amazon.com/s3/buckets/knowledgeproject?prefix=coffee-logging/&region=us-west-1

#* Cleaning
pycache-remove: ## cleanup subcommand - pycache-remove
	find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

dsstore-remove: ## cleanup subcommand - dsstore-remove
	find . | grep -E ".DS_Store" | xargs rm -rf

mypycache-remove: ## cleanup subcommand - mypycache-remove
	find . | grep -E ".mypy_cache" | xargs rm -rf

ipynbcheckpoints-remove: ## cleanup subcommand - ipynbcheckpoints-remove
	find . | grep -E ".ipynb_checkpoints" | xargs rm -rf

pytestcache-remove: ## cleanup subcommand - pytestcache-remove
	find . | grep -E ".pytest_cache" | xargs rm -rf

shell:
	docker exec -it [CONTAINER_ID] /bin/bash

test:
	docker exec -it [CONTAINER_ID] pytest

# build-remove: ## remove generated files/dirs
# 	rm -rf frontend-dashboard/.parcel-cache/
# 	rm -rf frontend-dashboard/dist/
# 	rm -rf frontend-dashboard/node_modules/
# 	rm frontend-dashboard/package-lock.json

# cleanup: build-remove pycache-remove dsstore-remove mypycache-remove ipynbcheckpoints-remove pytestcache-remove
cleanup: pycache-remove dsstore-remove mypycache-remove ipynbcheckpoints-remove pytestcache-remove
