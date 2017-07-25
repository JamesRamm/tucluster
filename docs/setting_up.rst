

Setting Up
===========


Configuration
-------------

TuCluster comes with a default configuration suitable for development, but for running in production
you will want to create a configuration file. This is a simple JSON file. You should create an environment
variable called ``TUCLUSTER_CONFIG`` which points to its' location.

Tucluster will override the default configuration with the contents of this file.

Example config file:

.. code-block:: JSON

    {
        "MONGODB": {
            "db": "tucluster",
            "host": "127.0.0.1",
            "port": 27017
        },
        "MODEL_DATA_DIR": "/path/to/data/dir",
        "TUFLOW_EXES": {
            'Tuflow Classic': 'tuflow',
        }
    }


Here is an explanation of the keys in the above config:

:MONGODB:
    This defines the database connection details. When you installed mongodb, you should've
    created a database; in the above configuration we have called this "tucluster".
    If you secured your database, you can add a ``"username"`` and ``"password"`` attribute
    after the ``"port"``

:MODEL_DATA_DIR:
    This is path to the root directory to where all model data should be put.
    This is the user uploaded input data and the result data created by e.g. tuflow.
    Therefore, you should ensure there is enough space to support your modelling needs.
    All the nodes in your cluster need to be able to access this path, so you will typically
    use some form of distributed file system. You should choose a file system with the lowest
    possible latency and that is easily scaled as your model output grows.

    Once Tucluster is running, you should *never* interact directly with this folder. TuCluster
    will manage the storage, upload and download of files. Manually adding/removing files could
    cause exceptions in TuClusters' execution.

:TUFLOW_EXES:
    This is a key: value list of all the Tuflow executables available on *each* worker node.
    The key is the human-readable identifier or name of the tuflow version and the value is the
    full path (or just name of the executable on linux) to the executable.

Running TuCluster
-----------------

You should use a production-ready web server such as GUnicorn to run tucluster.
Running with GUnicorn is easy::

    gunicorn tucluster.app

This will run tucluster on port 8000. You would normally configure a proxy such as NGinx to allow
external requests.

You will then need to run the tucluster celery app on each worker node:

    celery -A qflow worker -l info

Run the above command on each server which you wish to execute tuflow models (remember; you will need to
install tucluster on each of these nodes aswell!).

You are now ready to start interacting with TuCluster
