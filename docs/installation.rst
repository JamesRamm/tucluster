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
- One or more worker 'nodes' (computers) which will run the Tucluster worker service and execut Tuflow models. Each node should have a licensed version of tuflow installed.

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
