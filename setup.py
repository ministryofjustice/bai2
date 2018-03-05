#!/usr/bin/env python
# -*- coding: utf-8 -*-
import importlib
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.rst') as readme_file:
    readme = readme_file.read().strip()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '').strip()

package_info = importlib.import_module('bai2')

install_requires = []
tests_require = ['flake8']
if sys.version_info[0:2] < (3, 4):
    install_requires.append('enum34')

setup(
    name='bai2',
    version=package_info.__version__,
    author=package_info.__author__,
    author_email=package_info.__email__,
    url='https://github.com/ministryofjustice/bai2',
    license='MIT',
    description='BAI2 Parser',
    long_description=readme + '\n\n' + history,
    packages=['bai2'],
    package_dir={'bai2': 'bai2'},
    include_package_data=True,
    keywords='bai2 bookkeeping cash management balance reporting',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='tests',
)
