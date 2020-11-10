.PHONY: help clean test test-all coverage release

help:
	@echo "Using make is entirely optional; these are simply shortcuts"
	@echo "See README.rst for normal usage."
	@echo ""
	@echo "clean - remove all build and test artifacts"
	@echo "test - run all tests using current python environment"
	@echo "test-all - run all tests in all supported python environments"
	@echo "coverage - check code coverage while running all tests using current python environment"
	@echo "release - NOT NORMALLY USED; See README.rst for release process"

clean:
	rm -fr build/ dist/ .eggs/ .tox/ .coverage
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

test: clean
	python setup.py test

test-all: clean
	pip install tox
	tox

coverage: clean
	pip install coverage
	coverage run setup.py test
	coverage report --show-missing

release: clean
	python setup.py sdist bdist_wheel upload
