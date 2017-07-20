=========
TuCluster
=========

HTTP API for managing and running Tuflow models in the cloud or a local HPC cluster.


.. image:: https://img.shields.io/travis/JamesRamm/tucluster.svg
        :target: https://travis-ci.org/JamesRamm/tucluster

.. image:: https://readthedocs.org/projects/tucluster/badge/?version=latest
        :target: https://tucluster.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/JamesRamm/tucluster/shield.svg
     :target: https://pyup.io/repos/github/JamesRamm/tucluster/
     :alt: Updates


* Free software: GNU General Public License v3

Quickstart
-----------

- Start the server: ``gunicorn tucluster.app``
- Start a celery worker: ``celery -A qflow worker -l info``

I reccomend installing HTTPie to interact on the command line.
