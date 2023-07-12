Methods - The Admin
===================

All source code in a project is separated into one or more files
called *methods*.

This chapter shows how to name methods, where to store them, how to
limit execution of them, and how to use a specific Python virtual
environments for any method.


Method Directories and Method Names
-----------------------------------

Methods (and build scripts @@ref) are stored in *method directories*.
Method directories are python packages (@@ref), and must be named
uniquely.  There can be any number of method directories in a project.

Method directories are made available to a project by specifying them
in ``accelerator.conf`` (@ref).

Formally, a method directory is

- a directory reachable by the Python interpreter that
- contains the (empty) file ``__init__.py``, and
- is listed under ``method packages`` in the ``accelerator.conf`` file.

Method directories are created by the ``ax init`` command (but can of
of course be created manually by following the above rules).

.. tip:: The ``ax method`` command provides information about methods and directories.

Here's an example of what a method directory may contain (read on for
more information)::

  dev/
      __init__.py   # mandatory
      methods.conf  # optional
      a_test.py     # a method
      bogus.py      # an ignored python file (no "a_"-prefix)
      test.txt      # ignored

Methods stored in a method directory must start with the string
``a_``, so for example the ``a_csvimport.py`` is a valid method
filename, but ``bogus.py`` is not.  The mandatory prefix might seem
awkward, but it is there for safety and convenience reasons.  Exax is
importing all python files in all method directories, and irrelevant
(and perhaps syntactically broken) files should never be considered
for execution.



Enabling method directories in ``accelerator.conf``
---------------------------------------------------

To make a method directory visible to exax, it has to be included in
``accelerator.conf``.  Here's an example

.. code-block::
   :caption: Example snippet from ``accelerator.conf``.

    method packages:
        dev auto-discover
        accelerator.standard_methods

In the above example, two method directories are enabled, ``dev`` and
``accelerator.standard_methods``.  The latter is included in the
source distribution and should typically be enabled.

Note the ``auto-discover`` keyword after ``dev``.  It tells exax to
include *all* methods (files matching the glob pattern ``a_*.py``) in
the ``dev`` method directory automatically.  This is typically what a
developer wants and expects, but in some scenarios it is better
to restrict access to a fixed set of methods, and this is the topic of
the next section.



Execution restriction and interpreter selection
-----------------------------------------------

A file named ``methods.conf`` can be put in a method directory to
limit execution to a set of explicitly specified methods.  This is
useful for example in a production environment where strict control of
what is executable is a requirement.

In addition, the ``methods.conf`` file can also be used to specify
independent Python interpreters for each method!  This means that each
method can run on its own Python version, and each method can use its
own virtual environment.  So if there is code that only runs on a
specific version of *pyTorch* for example, this is straightforward to
manage!

If no ``methods.conf`` is present, all methods in the method directory
are assumed to be executable using the default Python interpreter.

.. code-block::
   :caption: Example ``methods.conf`` file.

   # This is a comment
   import_data        tf212    # use the "tf212" interpreter / virtual environment
   train_network               # use the default interpreter
   
Interpreters must be defined in ``accelerator.conf`` (@@@).

.. note:: Methods are listed *without* the ``a_`` prefix and ``.py`` suffix in ``methods.conf``!

.. note:: Access restriction is disabled if ``auto-discover`` is enabled
          for the directory in ``accelerator.conf`` (r@@).  Interpreter selection is still active, though.  (@@right?)
