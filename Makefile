.PHONY: help clean test test-all coverage lint release

help:
	@echo "Using make is entirely optional; these are simply shortcuts"
	@echo "See README.rst for normal usage."
	@echo ""
	@echo "clean - remove all build and test artifacts"
	@echo "test - run all tests using current python environment"
	@echo "test-all - run all tests in all supported python environments"
	@echo "coverage - check code coverage while running all tests using current python environment"
	@echo "lint - check code style"
	@echo "release - NOT NORMALLY USED; See README.rst for release process"

clean:
	rm -fr build/ dist/ .eggs/ .tox/ .coverage
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

test:
	python -m tests

test-all:
	pip install --upgrade tox
	tox

coverage:
	pip install --upgrade coverage
	coverage run setup.py test
	coverage report --show-missing

lint:
	pip install -r requirements-lint.txt
	flake8 --verbose

release: clean
	pip install --upgrade twine
	python setup.py sdist bdist_wheel
	twine upload dist/*
