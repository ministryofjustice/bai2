.PHONY: help init clean test test-all coverage lint release

help:
	@echo "Using make is entirely optional; these are simply shortcuts"
	@echo "See README.rst for normal usage."
	@echo ""
	@echo "init - create virtual environment"
	@echo "clean - remove all build and test artifacts"
	@echo "test - run all tests using current python environment"
	@echo "test-all - run all tests in all supported python environments"
	@echo "coverage - check code coverage while running all tests using current python environment"
	@echo "lint - check code style"
	@echo "release - NOT NORMALLY USED; See README.rst for release process"

init:
	[ -d venv ] || python -m venv venv
	./venv/bin/pip install -U setuptools pip wheel
	./venv/bin/pip install --editable .
	@echo `./venv/bin/python --version` virtual environment installed. Activate it using '`. ./venv/bin/activate`'

clean:
	rm -fr build/ dist/ .eggs/ .tox/ .coverage
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

test:
	pip install --editable .
	python -m tests

test-all:
	pip install --upgrade tox
	tox

coverage:
	pip install --upgrade coverage
	coverage run tests
	coverage report --show-missing

lint:
	pip install -r requirements-lint.txt
	flake8 --verbose

release: clean
	pip install build twine
	python -m build
	twine upload dist/*
