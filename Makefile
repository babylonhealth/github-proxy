NAME=github-proxy
LOCAL_REDIS_CONTAINER_NAME=$(NAME)-redis
LOCAL_REDIS_PORT=6379
MAX_LINE_LENGTH=88

build: setup-poetry
	poetry build

clean:
	find . -name "*.py[cod]" -delete

format:
	black .
	isort .

lint:
	flake8 --max-line-length $(MAX_LINE_LENGTH) --ignore=E203,W503
	black . --check
	isort . --check-only

typecheck:
	mypy --package github_proxy --strict

setup-poetry:
	pip3 install "tomlkit>=0.7.2" "poetry-dynamic-versioning==0.16.0"
	poetry config repositories.babylon https://artifactory.ops.babylontech.co.uk/artifactory/api/pypi/babylon-pypi
	poetry config http-basic.babylon $(ARTIFACTORY_PYPI_USER) $(ARTIFACTORY_PYPI_API_KEY)

install: setup-poetry
	poetry install -E flask -E redis

test-unit:
	pytest -vvv --mypy --cov github_proxy --cov-report xml --cov-report term tests/unit

test-integration:
	pytest -vvv --mypy tests/integration


local-redis:
	docker run --rm -d -p $(LOCAL_REDIS_PORT):6379 --name $(LOCAL_REDIS_CONTAINER_NAME) redis

stop-local-redis:
	docker stop $$(docker ps -a -q --filter="name=$(LOCAL_REDIS_CONTAINER_NAME)")

dist: clean build
	ls -l dist

release: dist
	poetry publish -r babylon --no-interaction

.PHONY: run clean format lint typecheck setup-poetry install test test-unit test-integration local-redis stop-local-redis
