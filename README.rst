=========
TuCluster
=========

HTTP API for managing and running Tuflow models in the cloud or a local HPC cluster.

.. note:: TuCluster is in early stages of development and not yet ready for production use.
        We are working towards a 0.1 release asap!


.. image:: https://img.shields.io/travis/JamesRamm/tucluster.svg
        :target: https://travis-ci.org/JamesRamm/tucluster

.. image:: https://pyup.io/repos/github/JamesRamm/tucluster/shield.svg
     :target: https://pyup.io/repos/github/JamesRamm/tucluster/
     :alt: Updates

Features
--------

- Upload Tuflow model data and queue models for execution across multiple workers
- Basic validation of control files
- Persists model metadata in mongodb allowing management and searching of all your modelling activities
- Poll running models for their status

Future
------
This API is very young and we have many ideas for expanding. Here is a rough roadmap of what we would like to achieve:

- Result exploration and data download (obviously a priority and being worked on right now!)
- Update models with new input data and re-run
- User accounts
- Email on result/failure
- Searching of models via various attributes (date, user etc)
- Spatial searching of models based on model boundary

The following are ideas for tucluster which may be moved to other projects/their own projects:

- Automatic discovery, download and management of DTM data. This will negate the need for expensive data uploads from the client
- Tiling of results for web maps
- Stitching results to a coherent raster based on a search area
- Realtime monitoring via websockets. (To be shunted over to the client side front-end project)

If you have any other feature ideas, please raise an issue.


Quickstart
-----------

- Start the server: ``gunicorn tucluster.app``
- Start a celery worker: ``celery -A qflow worker -l info``

You can now interact with the API using e.g. HTTPie

Endpoints
---------

- ``/models``
        - GET: Returns a list of all models that have been created. A model has a name, description and a folder containing all tuflow model input files
        - POST: Upload a single zip archive containing all model data. TCF files must be in the root directory. Returns a representation of the
                created model.

- ``/models/{name}``
        - GET: Retrieve a representation of single model by its name
        - PUT: Update the ``name`` and ``description`` of a single model.

- ``/runs``
        - GET: Returns a list of all model runs. A model run represents a single execution of a Tuflow model.
        It has a link to its model, a control file, the name of the tuflow executable and a task id.
        The task id can be used to query the status of the run. Upon completion the location of the
        results, log and check folders are available in the model run.

        - POST: Start a tuflow modelling task. A representation of the created model run is returned. POST body should be json containing:
                - ``tuflowExe`` - the name of the tuflow executable to use for this run
                - ``modelName`` - the name of the parent model which supplies the input data
                - ``controlFile`` - the path to the control file to use for this run (taken from the parent model)

- ``/runs/{oid}``
        - GET: Retrieve a representation of a single model run by its' ID.

- ``/tasks/{id}``
        - GET: Retrieve the current status of a task by its task_id. A task is a currently-executing model run
        and the task id can be retrieved from the model run object.

Licence
--------

Tucluster is licensed under the GPLv3