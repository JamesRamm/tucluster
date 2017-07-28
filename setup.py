#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'falcon==1.2.0',
    'mongoengine==0.13.0'
]

dependency_links = [
    'git+https://github.com/JamesRamm/qflow#egg=qflow'
]

setup_requirements = [
    'pytest-runner'
]

test_requirements = [
    'pytest'
]

setup(
    name='tucluster',
    version='0.1.0',
    description="HTTP API for managing and running Tuflow models in the cloud",
    long_description=readme + '\n\n' + history,
    author="James Ramm",
    author_email='jamessramm@gmail.com',
    url='https://github.com/JamesRamm/tucluster',
    packages=find_packages(include=['tucluster']),
    include_package_data=True,
    install_requires=requirements,
    dependency_links=dependency_links,
    license="GNU General Public License v3",
    zip_safe=False,
    keywords='tucluster',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
