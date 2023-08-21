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


Start an exax server
--------------------

.. code-block::

   ax server


Run the Tutorial and Other Examples
-----------------------------------

Start a new project with example files (see above).  Then check the
contents in the ``examples`` directory and run for example

.. code-block::

   ax run tutorial01


Enable the *exax Board* web server
----------------------------------

Open the ``accelerator.conf`` file (@) in an editor and edit the
``board listen`` line similar to this

.. code-block::

   board listen: localhost:8888

Then restart the server.  This will make the exax Board server listen
to port 8888 on the current machine.  Start a web browser and point it
to ``http://localhost:8888`` to view the content.


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
