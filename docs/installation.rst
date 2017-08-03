.. highlight:: shell

============
Installation
============

Getting Prepared
----------------
TuCluster is a distributed/cloud service for running flood models. A typical setup will have at least
2 hardware servers: One server on which the TuCluster API runs and one or more 'worker nodes' which
are responsible for running Anuga/Tuflow and receiving tasks.
(For local development, you will typically install everything onto your single development computer.)

Setting Up The Main Server
--------------------------

You will need to install `Redis<https://redis.io/>`_ and `MongoDB<https://www.mongodb.com/>`_.
Redis is a message queue which will pass instructions from your main server to each worker node.
MongoDB is a NoSQL database which will store metadata about your models.

After installation of Redis and MongoDB, you can go ahead and install TuCluster:

To install the latest stable release, run this command in your terminal:

.. code-block:: console

    $ pip install tucluster

If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

Note that TuCluster is only compatible with Python 3.5 and above. We recommend installing into a virtualenv.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


Setting up the Workers
----------------------

For each worker we will install:

- TuCluster (tucluster contains both the main server API and the celery worker application. We will use different commands to start running the different apps)
- ANUGA

You can install Tucluster as above (if your worker node and main server are the same, there is no need to install twice!)

ANUGA Setup
***********

In order to run ANUGA without conflicts with Tucluster library, TuCluster expects that
ANUGA is installed into a conda environment called 'anuga'.

1. Install Miniconda on each of your worker nodes. (https://conda.io/miniconda.html)
2. Create a new environment and install the dependencies:
    ```
    conda create -n anuga python=2 pip nomkl nose numpy scipy matplotlib netcdf4
    source activate anuga
    conda install -c pingucarsti gdal
    export GDAL_DATA=`gdal-config --datadir`
    ```

3. Clone Anuga to a suitable location on the worker: ``git clone https://github.com/GeoscienceAustralia/anuga_core``
4. ``cd`` into the anuga directory and install:
    ```
    python setup.py build
    sudo python setup.py install
    ```

It should be noted that all the nodes in the cluster (workers and server) should have a common file system in which the modelling data and results will be placed.
