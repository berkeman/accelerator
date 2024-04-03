Build Scripts
=============

Build scripts are the top level Python programs that control the
execution flow of a project.  Build scripts execute methods, assign
parameters, and pass results and intermediate data from previous
executions to the next.  In general, any code can be executed by a
build script.


Build Scripts Create Jobs
-------------------------


Execution of a build script will *always* result in the creation of a
new job, i.e. a directory where source code and all details relating
to the execution of the build script is stored on disk.  This is
different for method execution, where directories are created *only*
for combinations of source code and input parameters that have not
been seen before.

..
   The data stored in a job directory is accessible using the ``ax job``
   shell command as well as from a web browser using the accelerator
   *board*.

   In addition, all jobs built in a build script



   @Jobs are built using the ``urd.build()`` call.  The first argument to
   @the call is the name of the method to be executed, and the remaining
   @arguments are either input parameters to the method or to the build
   @process itself.



The Minimal Build Script
------------------------

All build script must contain a function ``main()``, that provides one
object called ``urd``, like this:

.. code-block::
   :caption: Minimal build script.

   def main(urd):
       # do something here...

The ``main()``-function is called when the build script is executed,
and the provided ``urd``-object contains parameters and useful helper
functions.

.. tip :: In a setup of a project with ``ax init`` using default
          parameters, build scripts are stored in the ``dev/``
          directory.  A minimal build script is part of the setup by
          default.


Build Script Naming and Execution
---------------------------------

Build scripts are stored along methods in method packages, and are
identified by filenames starting with the string "``build_``", except
for the "default" build script that is simply named ``build.py``.  The
default build script is executed using the shell command ``ax run``,
and any other build script, such as for example ``build_something.py``
is executed using ``ax run something``, and so on.

.. code-block::
    :caption: run the default ``build.py`` build script

    ax run

.. code-block::
    :caption: run the ``build_myscript.py`` build script

    ax run myscript

.. tip :: All available buildscripts can be listed along with
  descriptions using the ``ax script`` command.

The ``ax run`` command will print its progress to standard out, including
the *job ids* of all jobs created or re-used.

.. note :: Remember, *every execution of a build script results in a
   new job stored on disk*.  This happens even if there are no changes
   to the script.  *This behaviour is different from the execution of
   methods*, which are re-executed if and only if there are any
   changes to the source code or its input parameters.

.. tip:: The data stored in a job directory is accessible using the
   ``ax job`` shell command, as well as from a web browser listening
   to the included accelerator *board* web server.


Building Jobs from Methods
--------------------------

The typical use of build scripts is to build jobs by executing methods
(i.e smaller Python programs), where data and results may be passed
from one job to the next.  Using methods, a complicated project can be
efficiently broken down in to smaller independent parts.

Jobs are built using the ``urd.build()`` call.  The first argument to
the call is the name of the method to be executed, and the remaining
arguments are either input parameters to the method or to the build
process itself.

The output from the build call is a *job object* that can be used to
access data in the job.  The object can be passed to other build calls
so that the next execution gets access to the data in the existing
job.

Here are some basic examples

.. code-block::
    :caption: Build script running ``awesome_method`` with and without option ``x=3``.

    def main(urd):
        urd.build('awesome_method')
        urd.build('awesome_method', x=3)

.. code-block::
    :caption: Pass reference to ``job1`` into ``next_method``.

    def main(urd):
        job1 = urd.build('awesome_method', x=3)
        job2 = urd.build('next_method', prev=job1)

.. code-block::
    :caption: Print data that a job returned

    def main(urd):
        job = urd.build('awesome_method')
	print(job.load())

The ``.build()`` function is just one of several class methods
provided by the ``urd`` object.  See the :ref:`Urd class documentation
<api:The Urd Class>` for full information.
