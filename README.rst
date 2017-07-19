=========
TuCluster
=========

HTTP API for managing and running Tuflow models in the cloud or a local HPC cluster.


.. image:: https://img.shields.io/pypi/v/tucluster.svg
        :target: https://pypi.python.org/pypi/tucluster

.. image:: https://img.shields.io/travis/JamesRamm/tucluster.svg
        :target: https://travis-ci.org/JamesRamm/tucluster

.. image:: https://readthedocs.org/projects/tucluster/badge/?version=latest
        :target: https://tucluster.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/JamesRamm/tucluster/shield.svg
     :target: https://pyup.io/repos/github/JamesRamm/tucluster/
     :alt: Updates


HTTP API for managing and running Tuflow models in the cloud


* Free software: GNU General Public License v3
* Documentation: https://tucluster.readthedocs.io.


Quickstart
-----------

- Start the server: ``gunicorn tucluster.app``
- Start a celery worker: ``celery -A qflow worker -l info``

I reccomend installing HTTPie to interact on the command line:

``http localhost:8000/models`` - return metadata on all tuflow models
``http POST localhost:8000/models @/path/to/model_data.zip`` - Upload a zip folder containing all inputs for a Tuflow model
``http localhost:8000/models/{name}`` - return metadata on a single model
