Build Scripts
=============

Build scripts are the top level Python programs that control the
execution flow of a project.  In general, any code can be executed by
a build script, and it is especially useful for executing job scripts,
and in the process assign parameters, and pass results and
intermediate data between jobs.

.. tip:: Build scripts are executed using the ``ax run`` command from
  the command line.


Build Scripts Create Jobs
-------------------------

Executing a build script will *always* result in the creation of a new
job, i.e. a directory where source code and all details relating to
the execution of the build script is stored on disk.  (This is
different for job script execution, where directories are created
*only* for combinations of source code and input parameters that have
not been seen before.)

.. note::

  Every time a build script is run, a new job is created, even if
  there are no changes to the build script.

.. tip::

   Data stored in a job directory is accessible using the ``ax job``
   shell command as well as from a web browser using the accelerator
   *board*.



The Minimal Build Script
------------------------

All build script must contain a function ``main()``, that provides one
object called ``urd``, like this:

.. code-block::
   :caption: Minimal build script.

   def main(urd):
       # do something here...

The ``main()``-function is called when the build script is executed,
and the provided ``urd``-object will then contain parameters and
useful helper functions.

.. tip :: In a setup of a project with ``ax init`` using default
          parameters, build scripts are stored in the ``dev/``
          directory.  The init command will create a minimal build
          script to look at by default.



Build Script Naming and Execution
---------------------------------

Formally, build scripts are stored along job scripts in method
packages, and are identified by filenames starting with the string
"``build_``", except for the "default" build script that is simply
named ``build.py``.  The default build script is executed using the
shell command ``ax run``, and any other build script, such as for
example ``build_something.py`` is executed using ``ax run something``,
and so on.  Here are three examples:

.. code-block::
    :caption: run the default ``build.py`` build script

    # run the default build script "build.py"
    ax run

.. code-block::
    :caption: run the ``build_myscript.py`` build script

    # run the build script "build_myscript.py"
    ax run myscript

.. code-block::
    :caption: Advanced: run build script from a particular method package

    ax run mypack
    ax run mypack.myscript

.. tip :: All available buildscripts can be listed along with
  descriptions using the ``ax script`` command.

The ``ax run`` command will print its progress to standard out, including
the *job ids* of all jobs created or re-used.

.. note :: Remember, *every execution of a build script results in a
   new job stored on disk*.  This happens even if there are no changes
   to the script.  *This behaviour is different from the execution of
   job scripts*, which are re-executed *if and only if* there are
   changes to the source code or its input parameters.

.. tip:: The data stored in a job directory is accessible using the
   ``ax job`` shell command, as well as from a web browser listening
   to the built in accelerator *board* web server.


Building Jobs from Job Scripts
------------------------------

The typical use of build scripts is to build jobs by executing job
scripts (i.e smaller Python programs), where data and results can be
passed from one job to the next.  Using job scripts, a complex project
can be efficiently broken down into smaller parts that are executed one
at a time.

.. note::
   In contrast to build scripts, job scripts are only re-executed when
   there are changes to source code or input parameters.

Jobs are built using the ``urd.build()`` call.  The first argument to
the call is the name of the job script to be executed, and the
remaining arguments are either input parameters to the job script or to
the build process itself.

The output from the build call is a *Job object* that can be used to
access data and parameters in the job.  The object can be passed to
other build calls so that the next execution gets access to the data
in a previous job.

Here are some basic examples

.. code-block::
    :caption: Build script running ``my_script`` with and without option ``x=3``.

    def main(urd):
        urd.build('my_script')
        urd.build('my_script', x=3)

.. code-block::
    :caption: Pass reference to ``job1`` into ``next_script``.

    def main(urd):
        job1 = urd.build('my_script', x=3)
        job2 = urd.build('next_script', prev=job1)

.. code-block::
    :caption: Print data that a job returned

    def main(urd):
        job = urd.build('my_script')
	print(job.load())

The ``.build()`` function is just one of several class methods
provided by the ``urd`` object.

.. See the :ref:`Urd class documentation <api:The Urd Class>` for full information.
