Quickstart
==========


Install
-------

.. code-block::

   pip install accelerator


Get help
--------

.. code-block::

   ax help

.. tip :: All ``ax``-command take the ``-h`` or ``--help`` option, for example ``ax init --help``!

Start a new project
-------------------

.. code-block::

   ax init <projectname>

with example files

.. code-block::

   ax init <projectname> --examples

.. tip:: If using a virtual environment, it is convenient to store it
   inside the project directory, like this::

      mkdir theproject
      cd theproject
      python3 -m venv venv
      source venv/bin/activate
      pip install accelerator
      ax init --force  # force, since the directory is not empty, it contains the venv-directory.



Start an exax server
--------------------

.. code-block::

   ax server


Enable the *exax Board* web server
----------------------------------

Open the ``accelerator.conf`` file (@) in an editor and edit the
``board listen`` line similar to this

.. code-block::

   board listen: localhost:8888

Then restart the server.  This will make the exax Board server listen
to port 8888 on the current machine.  Start a web browser and point it
to ``http://localhost:8888`` to view the content.


Run the Tutorial and Other Examples
-----------------------------------

Start a new project with example files (see above).  Then check the
contents in the ``examples`` directory and run for example

.. code-block::

   ax run tutorial01


Show available method directories, methods and descriptions
-----------------------------------------------------------

.. code-block::

  ax method


Show build scripts and descriptions
-----------------------------------

.. code-block::

   ax script


Run a specific build script
---------------------------

A script named ``build_myprogram.py`` is run by omitting the
``build_``-prefix like this

.. code-block::

   ax run myprogram


Write new code
--------------

By default, the ``ax init`` program creates a method package in a
directory named ``dev/``. New methods and build scripts can be
executed if stored there.  Methods are stored using the filename
prefix ``a_`` (e.g. ``a_mymethod.py``), and build scripts use the prefix
``build_`` (e.g. ``build_myscript.py``).
