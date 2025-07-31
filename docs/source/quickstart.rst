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

.. tip :: All ``ax``-commands take the ``-h`` or ``--help`` option, for example ``ax init --help``!

Start a new project
-------------------

.. code-block::

   ax init <projectname> --examples

The init-command will create a new directory containing everything
required to start using Exax.  The ``--examples`` argument is there to
include some examples and tutorial files in the project.

.. tip:: If using a virtual environment, it is convenient to store it
   inside the project directory, like this::

      mkdir <projectname>
      cd <projectname>
      python3 -m venv venv
      source venv/bin/activate
      pip install accelerator
      ax init --force

   Since there is no name after "ax init", the project will be
   initiated in the current ("newproject") directory.  The force flag
   is required here, since the directory is not empty, due to the
   "venv" directory.)

.. tip:: ``ax init --help`` for more information about project initiation.


Start an exax server
--------------------

Start the exax server like this:

.. code-block::

   ax server


Access the *exax Board* web server
----------------------------------

The command

.. code-block::

   ax board-server localhost:8888

will make the Board (web) server listen to port 8888.

Point a browser to http://localhost:8888 to connect.

.. tip:: The board server starts automatically when the exax server
         starts.  Modify the configuration file to set which port or
         socket it should listen to by default.


Show available build scripts
----------------------------

All build scripts will be listed by

.. code-block::

   ax script

The examples will show up here if selected at project initialisation.


Run the Tutorial and Other Examples
-----------------------------------

If initiated with examples, example files will be stored in the ``examples/``
directory.  Run examples like this

.. code-block::

   ax run tutorial01

.. note:: Build script filenames start with ``build_``.  Omit this
          prefix (and the ``.py``-suffix) when running them using ``ax run``.


Show available method directories, job scripts and descriptions
---------------------------------------------------------------

Job scripts are (typically) small programs that are run from a build
script.  Job scripts may include code that executes using parallel
processing.  List available job scripts like this

.. code-block::

  ax method

This will show a list of all standard job scripts that are bundled
with exax.  If initiated with ``--examples``, all example job scripts
will show up here as well.


Run a specific build script
---------------------------

A script named ``build_myprogram.py`` is run by omitting the
``build_``-prefix and ``.py``-suffix like this

.. code-block::

   ax run myprogram

.. tip::

   The default build script is just named ``build.py``, and executed
   simply using ``ax run``.



Packages and Filename Prefixes
------------------------------

By default, the ``ax init`` program creates a method package in a
directory named ``dev/``. This is where job and build scripts should
be stored in the new project, otherwise they cannot be executed by
exax.

Job scripts are stored using the filename prefix ``a_``
(e.g. ``a_mymethod.py``), and build scripts use the prefix ``build_``
(e.g. ``build_myscript.py``).



The Configuration File
----------------------

The configuration file, ``accelerator.conf``, is where paths to code,
input data, and output results are defined.  The file also specifies
which ports or sockets that the exax server and board server listens
to, and how many parallel processes that should be forked in case of
parallel processing.

For example, to change listening port for the board server, the
configuration file should have a line like this

.. code-block::

   board listen: localhost:8888

.. note:: The exax server needs to be restarted for the configuration
          file changes to apply.

.. tip:: If Exax runs on a remote machine, its board server can be
         accessed using ssh port forwarding.  A simple way is to let board
         connect to a socket, which is the default:

         .. code-block:: text

            board listen: .socket.dir/board

         then connect to the server using

         .. code-block:: bash

            ssh -L 8888:/path/to/project/.socket.dir/board server

	 and point a browser on the local machine to ``localhost:8888``.
