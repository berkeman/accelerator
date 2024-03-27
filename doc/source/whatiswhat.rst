Basic Terminology and Operation
===============================

Exax is a user-space client-server application.  There is one server
per project using exax.  A project's source code is separated into two
types of files:

  - *build scripts* and
  - *methods*.

While build scripts control execution on a higher level, methods
perform the core computations.  The terminology is that methods are
*built* from build scripts.  When a method is built, the result is a
*job*, which is a persistent set of files disk.  These files are
easily accessible from a build script, so that they can be presented
to the user or used as input to other method builds.

This section gives and overview, see chapters @@, @@ for detailed
information.

What is a Method?
-----------------

A *method* is a file containing Python code.  When executed (called
from a build script), exax will create a new directory on disk that is
associated with the build, and store everyting related to the build
process there.  This happens *unless* the same method has already been
built before, with the same inputs and parameters.  A method will
never be executed again if the result is known and available on disk.
The directory containing the build's information is called a *job* or
a *job directory*.

Methods can execute in a single process, and it is also possible to do
simple (but powerful) parallel processing.  Execution flow in a method
is set by a few pre-defined functions.

.. tip:: A 64-core CPU can do one CPU-core-hour of work in *less than
   one minute*, if workload is parallellised.  A common of the shelf
   inexpensive eight-core CPU can do the same work in just 7.5
   minutes!


..
   Method source files are stored in Python packages, meaning a directory
   that has an ``__init__.py`` file, see the Python documentation.

   .. note::
      The ``ax init`` will set up a Python package called ``dev`` by
      default, but it is trivial to add more packages if necessary.

   The naming of method files is special.  A method has to start with the
   prefix ``a_``.

   .. note:: The method ``mymethod`` is stored in a file named
	     ``a_mymethod.py``.

   This seems unusual, but there are good reasons for it.

All methods in a project can be listed using the ``ax method``
command, or be browsed in a web browser using the built in Board web
server.


What is a Job?
--------------

A *job* is a directory that is associated with the execution of a
method.  The directory contains input parameters, source code, output
files, and anything printed to standard out and standard error during
the execution.

Each job is associated a unique identifier, such as for example
``dev-37``.  This called the *job id*, and the directory where the
information is stored is called the *job directory*.

Job directories are stored in *workdirs*, which are nothing more than
ordinary directories.  The name and location of the workdirs are
defined in the configuration file.


What is a Build Script?
-----------------------

A build script is also a file containing Python code.  Build scripts
can execute *methods*, and thus create *jobs*.  Build scripts have
direct access to the data stored in job directories, so that they can
pass data and parameters from previous jobs to new builds.

The main purpose of the build script is to control the method
execution, and a typical project has at least one build script that
calls a set of methods in a particular order.

..
   Just like method files, the naming of build script files is also
   special.  A build script has to start with the prefix ``build_``.

   .. note:: The build script ``myscript`` is stored in a file named
	     ``build_myscript.py``.

   .. note:: The default build script is just ``build.py``.

All build scrips in a project can be listed using the ``ax script``
command, or be browsed in a web browser using the built in Board web
server.
