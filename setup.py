#!/usr/bin/env python
import importlib
import os
import sys
import warnings

from setuptools import setup

if sys.version_info[0:2] < (3, 7):
    warnings.warn('This package is tested with Python version 3.7+')

root_path = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(root_path, 'README.rst')) as readme:
    README = readme.read()

package_info = importlib.import_module('bai2')

install_requires = []
tests_require = []

setup(
    name='bai2',
    version=package_info.__version__,
    author=package_info.__author__,
    author_email='dev@digital.justice.gov.uk',
    url='https://github.com/ministryofjustice/bai2',
    packages=['bai2'],
    package_dir={'bai2': 'bai2'},
    include_package_data=True,
    license='MIT',
    description='BAI2 Parser',
    long_description=README,
    keywords='bai2 bookkeeping cash management balance reporting',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='tests',
)
