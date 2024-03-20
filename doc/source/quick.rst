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

      mkdir newproject
      cd newproject
      python3 -m venv venv
      source venv/bin/activate
      pip install accelerator
      ax init --force  # force, since the directory is not empty, it contains our venv-directory.



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
``build_``-prefix and ``.py``-suffix like this

.. code-block::

   ax run myprogram

.. tip::

   The default build script is just named ``build.py``, and executed
   simply using ``ax run``.



Write new code
--------------

By default, the ``ax init`` program creates a method package in a
directory named ``dev/``. New methods and build scripts can be
executed only if stored there.  Methods are stored using the filename
prefix ``a_`` (e.g. ``a_mymethod.py``), and build scripts use the
prefix ``build_`` (e.g. ``build_myscript.py``).  



Extra:  Configure the Board server to autostart
-----------------------------------------------

Open the ``accelerator.conf`` file (@) in an editor and edit the
``board listen`` line similar to this

.. code-block::

   board listen: localhost:8888

Then restart the server.  This will make the exax Board server listen
to port 8888 on the current machine.  Start a web browser and point it
to ``http://localhost:8888`` to view the content.

.. note:: The exax server needs to be restarted for the configuration
          file changes to apply.

.. tip:: If Exax runs on another machine, its board server can be
         accessed using port forwarding.  A simple way is to let board
         connect to a socket, which is the default:

         .. code-block:: ``accelerator.conf``:

            board listen: .socket.dir/board

         then connect to the server using

         .. code-block::

            ssh -L 8888:/path/to/project/.socket.dir/board server
