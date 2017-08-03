.. highlight:: shell

============
Installation
============

Getting Prepared
----------------
Before installing TuCluster, you need to make sure you have the infrastructure and 3rd party
services/software required to run it.

You will need:

- A hardware server on which to run the Tucluster web service.
- A hardware server on which to run the MongoDB instance which will store tucluster metadata. This will most likely be the same hardware that runs Tucluster, although you may wish to use a 3rd party service such as MongoDB Atlas
- A hardware server on which to run the Redis message queue. This is responsible for queuing modelling tasks to be consumed by workers. Again, this is usually the same hardware on which the Tucluster API runs.
- One or more worker 'nodes' (computers) which will run the Tucluster worker service and execut Tuflow models. Each node should have ANUGA or a licensed version of tuflow installed.

For local development, you will typically install everything onto your single development computer.

It should be noted that all the nodes in the cluster (workers and server) should have a common file system in which the modelling data and results will be placed.

You will need to install `Redis<https://redis.io/>`_ and `MongoDB<https://www.mongodb.com/>`_ on your server.
On each of your worker nodes, you will also need to install ANUGA and/or Tuflow.

For light loads on a self-hosted cluster, a typical simple setup would have the tucluster webservice, mongodb and redis all running on a single
hardware machine, with the tucluster worker on 1 or more separate machines with ANUGA and/or Tuflow installed:

```
    _________________
   |                 |
   | Tucluster server|
   | MongoDB         |
   | Redis           |
   |_________________|
           |
    _________________
   |                 |
   |Tucluster Worker |
   |ANUGA/Tuflow     |
   |_________________|
```


ANUGA Setup
------------

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

Now proceed to install tucluster.


Stable release
--------------

TuCluster requires python 3. If you have just installed ANUGA, be sure to ``deactivate`` the anuga environment
before install TuCluster (and create a new environment for python 3 if necessary)

To install TuCluster, run this command in your terminal:

.. code-block:: console

    $ pip install tucluster

This is the preferred method to install tucluster, as it will always install the most recent stable release.
You need to install TuCluster on all your worker nodes and the main web server.


If you don't have `pip`_ installed, this `Python installation guide`_ can guide
you through the process.

.. _pip: https://pip.pypa.io
.. _Python installation guide: http://docs.python-guide.org/en/latest/starting/installation/


From sources
------------

The sources for tucluster can be downloaded from the `Github repo`_.

You can either clone the public repository:

.. code-block:: console

    $ git clone git://github.com/JamesRamm/tucluster

Or download the `tarball`_:

.. code-block:: console

    $ curl  -OL https://github.com/JamesRamm/tucluster/tarball/master

Once you have a copy of the source, you can install it with:

.. code-block:: console

    $ python setup.py install


.. _Github repo: https://github.com/JamesRamm/tucluster
.. _tarball: https://github.com/JamesRamm/tucluster/tarball/master

