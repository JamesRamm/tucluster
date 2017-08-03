

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
        "TUFLOW_PATH": "tuflow",
        "ANUGA_ENV": "anuga"
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

:TUFLOW_PATH:
    Path to the Tuflow executable to use on each worker node. This implies that it should be the same
    on each node. If Tuflow is available globally on the system PATH, just enter the executable name

:ANUGA_ENV:
    Name of the conda environment in which ANUGA is installed.

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


Note on Using ANUGA
-------------------

Running python scripts on the server is potentially dangerous and you should ensure that your webserver
runs as a non-root user and restrict its permissions. Essentially, the only place it needs to be able to write files
is the directory you set as the ``MODEL_DATA_DIR`` in your configuration file.

Developers of ANUGA scripts should be aware of these restrictions and should set the ``datadir`` appropriately.
The best advice here is to set it relative to the script file. E.g:

``domain.set_datadir(os.path.dirname(__file__), 'results')``

ANUGA scripts should also be carefully developed so they do not hang. E.g. causing the script to display a
matplotlib figure or other GUI elements will prevent the script from terminating until the window has been manually closed.
You should not do this! Any figures should be output directly to file.
