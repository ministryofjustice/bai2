#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
]

# We only need enum34 for Pythons before 3.4
if sys.version_info < (3, 4):
    requirements.append('enum34')


test_requirements = [
    'mock',
]

setup(
    name='bai2',
    version='0.3.0',
    description="BAI2 Parser",
    long_description=readme + '\n\n' + history,
    author="MoJ",
    author_email='dev@digital.justice.gov.uk',
    url='https://github.com/ministryofjustice/bai2',
    packages=[
        'bai2',
    ],
    package_dir={'bai2':
                 'bai2'},
    include_package_data=True,
    install_requires=requirements,
    license="BSD",
    zip_safe=False,
    keywords='bai2',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
