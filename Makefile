PROJECT_NAME := wishlist
DOCKER_COMPOSE := docker compose

.PHONY: up down logs seed backend-shell frontend-shell test lint format build

up:
	$(DOCKER_COMPOSE) up --build

down:
	$(DOCKER_COMPOSE) down --remove-orphans

logs:
	$(DOCKER_COMPOSE) logs -f

seed:
	$(DOCKER_COMPOSE) run --rm backend python -m app.utils.seeder

backend-shell:
	$(DOCKER_COMPOSE) run --rm backend bash

frontend-shell:
	$(DOCKER_COMPOSE) run --rm frontend sh

test:
	$(DOCKER_COMPOSE) run --rm backend pytest

lint:
	$(DOCKER_COMPOSE) run --rm backend sh -c "ruff check . && black --check . && mypy app"
	$(DOCKER_COMPOSE) run --rm frontend npm run lint

format:
	$(DOCKER_COMPOSE) run --rm backend sh -c "ruff check --fix . && black ."
	$(DOCKER_COMPOSE) run --rm frontend npm run format

build:
	$(DOCKER_COMPOSE) build
