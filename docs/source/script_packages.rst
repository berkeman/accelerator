Script Packages
===============


Job and build scripts are stored in ordinary Python packages.  (A
Python package is a directory with Python files and a mandatory
``__init__.py`` file.)  In this context they are called *method
packages* or simply *method directories*.

This chapter explains method packages and how to name job and build
scripts, limit execution to certain set of job scripts, and use a
specific Python virtual environment or dedicated interpreter for any
job script.

.. tip:: If a project is set up with ``ax init`` using default
         options, all job and build scripts will be stored in the
         ``dev/``-directory.  Remember that job script filenames are
         prefixed with ``a_`` and build scripts are prefixed with
         ``build_``.



Method Packages and File Naming
-------------------------------

Method packages are made visible to a project by specifying them in
``accelerator.conf``.

Formally, a method package is

- a directory reachable by the Python interpreter that
- contains the (empty) file ``__init__.py``, and
- is listed under ``method packages`` in the ``accelerator.conf`` file.

Method packages are typically created by the ``ax init`` command (but
can of of course be created manually by following the above rules).

.. tip:: The ``ax method`` command provides information about
         existing job scripts.

.. tip:: the ``ax script`` command lists existing build scripts.

.. note::
   There can be any number of job scripts and method packages in a
   project, but *job script names must be unique*.

Here's an example of what a method package may contain (read on for
more information)

.. code-block::
  :caption: Example method package directory contents

  dev/
      __init__.py   # mandatory
      methods.conf  # optional, see below
      a_test.py     # a job script
      build_foo.py  # a build script
      bogus.py      # an ignored Python file (no "a_"-prefix)
      test.txt      # not a Python file, is also ignored

job script stored in a method package must start with the string
``a_``, so for example the ``a_csvimport.py`` is a valid filename, but
``bogus.py`` is not.  The mandatory prefix might seem awkward, but it
is there for safety and convenience reasons.  Exax is importing all
Python files in all method packages, and irrelevant (and perhaps
syntactically broken) files should never be considered for execution.

Similarly, build scripts stored in a method package must start with
the string ``build_``.  The only exception is the "default" build
script that goes simply by the name ``build.py``.



Enabling Method Directories in ``accelerator.conf``
---------------------------------------------------

To make a method package visible to exax, it has to be included in
``accelerator.conf``.  Here's an example

.. code-block::
   :caption: Example definition of method packages in ``accelerator.conf``.

    method packages:
        dev auto-discover
        accelerator.standard_methods

In the above example, two method packages are enabled, ``dev`` and
``accelerator.standard_methods``.  The latter is bundled as part of
the exax distribution and contains useful job scripts mainly for
dataset processing.  Note that method packages are listed using Python
package names, as seen by the Python interpreter, and not by file
system paths.

Note the ``auto-discover`` keyword after ``dev``.  It tells exax to
include *all* job scripts (files matching the glob pattern ``a_*.py``)
in the ``dev`` method directory automatically.  This is typically what
a developer wants and expects, but in some scenarios it is better to
restrict access to a fixed set of job scripts, and this is the topic of
the next section.



Execution Restriction and Interpreter Selection
-----------------------------------------------

An optional file named ``methods.conf`` in a method package is used to
limit execution to a set of explicitly specified job scripts.  This is
useful for example in a production environment where strict control of
what is executable is a requirement.

In addition, the ``methods.conf`` file can be used to specify
independent Python interpreters for each job script!  This means that
each job script can run on its own Python version, and each job script
can use its own virtual environment with unique dependencies and
versions.

.. tip:: Using ``methods.conf``, two different job scripts could for
         example use two different versions of *pyTorch* in the same
         project!

If no ``methods.conf`` is present, all job scripts in the method directory
are assumed to be executable using the default Python interpreter.

Here is an example of a ``methods.conf`` file:

.. code-block::
   :caption: Example ``methods.conf`` file.

   # This is a comment
   import                # job script import use the default interpreter
   train        tf212    # job script train uses the "tf212" virtual environment

Interpreters are defined in ``accelerator.conf`` like this

.. code-block::
   :caption: Example definition of interpreters in ``accelerator.conf``.

   interpreters:
         tf212  /home/ab/myaxproject/venv/bin/python
         p38    /usr/bin/python3.8

.. note:: Job scripts are listed *without* the ``a_`` prefix and ``.py``
          suffix in ``methods.conf``!

.. note:: Access restriction is disabled using the per-package
          ``auto-discover`` keyword in
          ``accelerator.conf``. *Interpreter selection is still active*,
          though.
