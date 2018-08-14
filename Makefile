.PHONY: help install install-dev start test
.DEFAULT_GOAL := help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort -k 1,1 | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install: ## Install production deps
	@docker-compose exec caluma pip install --upgrade -r requirements.txt

install-dev: ## Install development deps
	@docker-compose exec caluma pip install --upgrade -r requirements.txt -r requirements-dev.txt

start: ## Start development server
	@docker-compose up -d

test: ## Test project
	@docker-compose exec caluma flake8
	@docker-compose exec caluma pytest --no-cov-on-fail --cov --create-db
