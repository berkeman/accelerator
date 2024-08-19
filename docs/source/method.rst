Method Packages
===============


Methods and build scripts are stored in ordinary Python packages.  (A
Python package is a directory with Python files and an ``__init__.py``
file.) In this context they are called *method packages* or simply
*method directories*.

This chapter explains method packages and how to name methods and
build scripts, limit execution to certain set of methods, and use a
specific Python virtual environment or dedicated interpreter for any
method.

.. tip:: If a project is set up with ``ax init`` using default
         options, all methods and build scripts will be stored in the
         ``dev/``-directory.  To get started quickly, all you need to
         know is that method filenames are prefixed with ``a_`` and
         build scripts are prefixed with ``build_``.


Method Packages and File Naming
-------------------------------

Method packages are made available to a project by specifying them in
``accelerator.conf``.

Formally, a method package is

- a directory reachable by the Python interpreter that
- contains the (empty) file ``__init__.py``, and
- is listed under ``method packages`` in the ``accelerator.conf`` file.

Method packages are typically created by the ``ax init`` command (but
can of of course be created manually by following the above rules).

.. tip:: The ``ax method`` command provides information about
         existing methods and packages.

.. tip:: the ``ax script`` command lists existing build scripts.

.. note::
   There can be any number of methods and method packages in a
   project, but *method names must be unique*.

Here's an example of what a method package may contain (read on for
more information)

.. code-block::
  :caption: Example method package directory contents

  dev/
      __init__.py   # mandatory
      methods.conf  # optional
      a_test.py     # a method
      build_foo.py  # a build script
      bogus.py      # an ignored python file (no "a_"-prefix)
      test.txt      # not a python file, ignored

Methods stored in a method package must start with the string ``a_``,
so for example the ``a_csvimport.py`` is a valid method filename, but
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
``accelerator.standard_methods``.  The latter contains useful methods,
and is bundled as part of the exax distribution.  Again, method
packages are Python packages, visible to the Python interpreter, so
what is listed are Python package names, not file system paths.

Note the ``auto-discover`` keyword after ``dev``.  It tells exax to
include *all* methods (files matching the glob pattern ``a_*.py``) in
the ``dev`` method directory automatically.  This is typically what a
developer wants and expects, but in some scenarios it is better to
restrict access to a fixed set of methods, and this is the topic of
the next section.



Execution Restriction and Interpreter Selection
-----------------------------------------------

An optional file named ``methods.conf`` in a method package is used to
limit execution to a set of explicitly specified methods.  This is
useful for example in a production environment where strict control of
what is executable is a requirement.

In addition, the ``methods.conf`` file is also used to specify
independent Python interpreters for each method!  This means that each
method can run on its own Python version, and each method can use its
own virtual environment.

.. tip:: Using ``methods.conf``, two different methods could for
         example use two different versions of *pyTorch* in the same
         project!

If no ``methods.conf`` is present, all methods in the method directory
are assumed to be executable using the default Python interpreter.

.. code-block::
   :caption: Example ``methods.conf`` file.

   # This is a comment
   import_data        tf212    # use the "tf212" interpreter / virtual environment
   train_network               # use the default interpreter

Interpreters are defined in ``accelerator.conf`` like this

.. code-block::
   :caption: Example definition of interpreters in ``accelerator.conf``.

   interpreters:
         tf212  /home/ab/myaxproject/venv/bin/python
         p38    /usr/bin/python3.8

.. note:: Methods are listed *without* the ``a_`` prefix and ``.py``
          suffix in ``methods.conf``!

.. note:: Access restriction is disabled using the per-package
          ``auto-discover`` keyword in
          ``accelerator.conf``. Interpreter selection is still active,
          though.
