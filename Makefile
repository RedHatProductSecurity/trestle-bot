PYMODULE := trestlebot
TESTS := tests

all: develop lint test
.PHONY: all

develop:
	@poetry install	
	@poetry shell
.PHONY: develop

lint:
	@poetry lock --check
	@poetry run isort --profile=black --lines-after-imports=2 \
	--check-only $(TESTS) $(PYMODULE)
	@poetry run black --check $(TESTS) $(PYMODULE) --diff
	@poetry run mypy $(PYMODULE) $(TESTS)
	@poetry run flake8
.PHONY: lint

format:
	@poetry run isort --profile=black --lines-after-imports=2 $(TESTS) $(PYMODULE)
	@poetry run black $(TESTS) $(PYMODULE)
.PHONY: format

test:
	@poetry run pytest --cov --cov-config=pyproject.toml --cov-report=xml
.PHONY: test

test-code-cov:
	@poetry run pytest --cov=trestlebot --exitfirst --cov-config=pyproject.toml --cov-report=xml --cov-fail-under=85
.PHONY: test-code-cov

# https://github.com/python-poetry/poetry/issues/994#issuecomment-831598242
# Check for CVEs locally. For automated/scheduled checks, use dependabot. 
dep-cve-check:
	@poetry export -f requirements.txt --without-hashes | poetry run safety check --stdin
.PHONY: dep-cve-check

security-check:
	@poetry run bandit -r $(PYMODULE)
.PHONY: security-check

build: clean-build
	@poetry build
.PHONY: build

clean-build:
	@rm -rf dist
.PHONY: clean-build

clean:
	@git clean -Xdf
.PHONY: clean

publish:
	@poetry config pypi-token.pypi $(PYPI_TOKEN)
	@poetry publish --dry-run
	@poetry publish
.PHONY: publish

build-and-publish: build publish
.PHONY: build-and-publish