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
      ax init

   (Since there is no name after "ax init", the project will be
   initiated in the current ("newproject") directory.)

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

If initiated with examples, they will be stored in the ``examples/``
directory.  Run examples like this

.. code-block::

   ax run tutorial01

.. note:: Build script filenames start with ``build_``.  Omit this
          prefix when running them using ``ax run``.


Show available method directories, methods and descriptions
-----------------------------------------------------------

Methods are (typically) small programs that are run from a build
script.  Methods may include code that executes using parallel
processing.  List available methods like this

.. code-block::

  ax method


Run a specific build script
---------------------------

A script named ``build_myprogram.py`` is run by omitting the
``build_``-prefix and ``.py``-suffix like this

.. code-block::

   ax run myprogram

.. tip::

   The default build script is just named ``build.py``, and executed
   simply using ``ax run``.



Write new code, filename prefixes
---------------------------------

By default, the ``ax init`` program creates a method package in a
directory named ``dev/``. New methods and build scripts can be
executed only if stored there.  Methods are stored using the filename
prefix ``a_`` (e.g. ``a_mymethod.py``), and build scripts use the
prefix ``build_`` (e.g. ``build_myscript.py``).  



The configuration file
----------------------

The configuration file, ``accelerator.conf``, is where paths to code,
input data, and output results are kept.  It also specifies which
ports or sockets that the exax server and board server listens to.

For example, to change listening port for the board server, the
configuration file should have a line like this

.. code-block::

   board listen: localhost:8888

.. note:: The exax server needs to be restarted for the configuration
          file changes to apply.

.. tip:: If Exax runs on another machine, its board server can be
         accessed using port forwarding.  A simple way is to let board
         connect to a socket, which is the default:

         .. code-block::

            board listen: .socket.dir/board

         then connect to the server using

         .. code-block::

            ssh -L 8888:/path/to/project/.socket.dir/board server

	 and point a browser on the local machine to ``localhost:8888``.
