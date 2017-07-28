=====
Usage
=====

You interact with Tucluster via some form of web client. This could be a user-facing website
you create yourself (we are in the process of creating a client website for using TuCluster) or
via a command line tool such as cUrl or HTTPie. I reccomend the latter for command line usage.

Typical Workflow
----------------

When using TuCluster, you will typically follow a workflow similar to the following:

- Prepare an input zip folder. This is all the modelling input data and ANUGA scripts (or Tuflow control files). Note that
the scripts/control files should be in the root zip archive.

- Upload the zip archive to TuCluster to create a new Model.

- You may wish to update the description or name of your newly created model, or explore other models
  on the system. You can view the input data folder structure and download individual files.

- Start a new modelling task. In Tucluster, this is called a Model Run. Each model run has a parent
  Model, a modelling engine and an entrypoint to be used.
  An entrypoint is an ANUGA script or control file. The modelling engine is either ``'anuga'`` or ``'tuflow'``.
  The modelling task will then be added to the queue and executed in the background by one of the worker nodes.
  You can create as many modelling tasks as you like - they will simply be queued up and executed when a worker is available.

- Check the status of your modelling task. Each model run has a task id which can be used to check the status
  of the task and get the result location once it has successfully completed.

- Explore the results. Once the modelling task has completed, you can explore the result folder, aswell
  as the output of the tuflow checks and logs (or any other output you create from ANUGA).
  You can find specific files and download them to your local computer.

- Explore historic models and runs. The metadata for all Models and model runs are tagged with dates and users
  so you can easily get a record of data provenance or build up an overview of what models you have available.
  You may mark a model run within a model as the ``baseline`` run for a given model.

We will now review each of the above points in detail and explain how to interact with TuCluster to achieve them.
