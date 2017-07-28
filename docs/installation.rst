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

It is up to you what configuration you use and will depend on both the number of tuflow license you have available and the anticipated workload.
You may choose to run Tucluster on local hardware within your own network or make use of cloud services such as Amazons' EC2.

It should be noted that all the nodes in the cluster (workers and server) should have a common file system in which the modelling data and results will be placed.

You will need to install `Redis<https://redis.io/>`_ and `MongoDB<https://www.mongodb.com/>`_ on your server.

Once this is done, you can install tucluster.

Stable release
--------------

To install tucluster, run this command in your terminal:

.. code-block:: console

    $ pip install tucluster

This is the preferred method to install tucluster, as it will always install the most recent stable release.

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

ANUGA Setup Notes
-----------------

In order to run ANUGA without conflicts with Tucluster library, TuCluster expects that
ANUGA is installed into a conda environment called 'anuga'.

You should setup this environment on each worker node and install ANUGA into it.
ANUGA comes with tools for installing into a conda environment (https://github.com/GeoscienceAustralia/anuga_core/blob/master/tools/install_conda.sh)

Running python scripts on the server is potentially dangerous and you should ensure that your webserver
runs as a non-root user and restrict its permissions. Essentially, the only place it needs to be able to write files
is the directory you set as the ``MODEL_DATA_DIR`` in your configuration file.

Developers of ANUGA scripts should be aware of these restrictions and should set the ``datadir`` appropriately.
The best advice here is to set it relative to the script file. E.g:

``domain.set_datadir(os.path.dirname(__file__), 'results')``

ANUGA scripts should also be carefully developed so they do not hang. E.g. causing the script to display a
matplotlib figure or other GUI elements will prevent the script from terminating until the window has been manually closed.
You should not do this! Any figures should be output directly to file.

A user could still potentially write a malicious script which will delete the ``MODEL_DATA_DIR`` and future work
will look at solutions to this problem.

