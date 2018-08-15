.PHONY: help install install-dev start test
.DEFAULT_GOAL := help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort -k 1,1 | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install: ## Install production environment
	@pip install --upgrade -r requirements.txt .

install-dev: ## Install development environment
	@pip install --upgrade -r requirements.txt -r requirements-dev.txt .

start: ## Start the development server
	@docker-compose up -d

test: ## Test the project
	@flake8
	@pytest --no-cov-on-fail --cov --create-db
