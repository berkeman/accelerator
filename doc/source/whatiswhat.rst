Basic Terminology and Operation
===============================

Exax is a user-space client-server application.  There is one server
per project using exax.  A project's source code is partitioned into
two types of files:

  - *build scripts*, and
  - *methods*.

*Build scripts* control the high level execution, and are responsible
for executing *methods*, that perform the core computations.  All code
execution, be it build scripts or methods, produce *jobs*, which are
composed of sets of files stored persistently on disk.  These files
contain everything related to the build script or the method's
execution, including input and output data, parameters, and source
code.  A job's files are easily accessible from a build script, so
that they can be presented to the user or used as input to other
method builds.

This section gives and overview, see chapters @@, @@ for detailed
information.



What is a Job?
--------------

A *job* is a directory that was created when a method or build script
was executed.  The directory contains a set of files containing input
parameters, source code, output files, profiling information, and
anything printed to standard out and standard error during the
execution.

Each job is associated a unique identifier, such as for example
``dev-37``.  This called the *job id*, and the directory where the
information is stored is called the *job directory*.

Job directories are stored in *workdirs*, which are just ordinary
directories.  The name and location of the workdirs are defined in the
configuration file.

For convenience, job directories are represented by job objects during
code execution.  There objects contain helper functions to access the
job's files and parameters.



What is a Build Script?
-----------------------

A project needs to have at least one build script.  A build script is
a Python file responsible for the top level execution flow of a whole
project or a subproject.

The main purpose of a build scripts is to execute methods and pass
data and parameters between them and the build script itself.

Execution of a build script *always* results in the creation of a job,
so it is always possible to go back and see what scripts that have
been executed in the past, as well as what input they used and output
they generated.

.. tip:: The naming of build script files is special.
	 A build script has to start with the prefix ``build_``.

	 The build script ``myscript`` is stored in a file named ``build_myscript.py``.

   .. note:: The default build script is just ``build.py``.

All build scrips in a project can be listed using the ``ax script``
command, or be browsed in a web browser using the built in Board web
server.



What is a Method?
-----------------

A project typically has one or more methods.  A method is a Python
script that is executed either from a build script or from another
method.

The first time a certain method is executed, exax creates a job
directory where it stores information throughout the execution.  When
execution finishes, exax will return a pointer to the created job.

On the other hand, if the method has already been executed in the
past, using the same inputs and parameters, exax will *not* create a
new job directory.  Instead, the execution will immediately return a
pointer to the existing job.

.. note:: A method will never be executed more than once for a given
          set of inputs and parameters.  Existing results will be
          re-used and not re-computed.

Methods can execute in a single process, and it is also possible to do
simple (but very powerful) *parallel processing*.  Execution flow in a
method is controlled by a few pre-defined functions.

.. tip:: A machine equipped with 64 core can do one CPU-core-hour of
   work in *less than one minute*, if workload is parallellised.  A
   more common of the shelf inexpensive eight-core CPU can do one CPU
   hour of work in just 7.5 minutes!

All methods in a project can be listed using the ``ax method``
command, or be browsed in a web browser using the built in Board web
server.




