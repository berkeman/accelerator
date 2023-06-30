Methods - The Admin
===================

This chapter shows how to name methods, where to store them, how to
limit access to them, and how to use a specific Python virtual
environments for any method.


Method Directories and Method Names
-----------------------------------

A method directory is where exax is looking for methods and build
scripts.  Method directories must be named uniquely, and there can be
any number of method directories in a project.

Formally, a method directory is

- a directory reachable by the Python interpreter that
- contains the (empty) file ``__init__.py``, and
- is listed under "``method packages``" in the ``accelerator.conf`` file.

Method directories are created by the ``ax init`` command (but can of
of course be created manually following the rules above as well).  The
``ax method`` command provides information about methods and
directories.

Here's an example of what a method directory may contain (read on for
more information)::

  dev/
      __init__.py   # mandatory
      methods.conf  # optional
      a_test.py     # a method
      bogus.py      # an ignored python file (no prefix)
      test.txt      # ignored

Methods stored in a method directory must start with the string
"``a_``", so for example the ``a_csvimport.py`` is a valid method
filename.  The mandatory prefix is for safety and convenience reasons.
Exax is importing all python files in all method directories, and
irrelevant (and perhaps syntactically broken) files should never be
considered for execution.



Method file naming, access restriction, and interpreter selection
-----------------------------------------------------------------

A file named ``methods.conf`` can be put in a method directory to
limit execution to a set of explicitly specified methods.  This can
make sense for example in a production environment where strict
control of what is executable is a requirement.

In addition, the ``methods.conf`` file can also be used to specify
independent Python interpreters for each method!  This means that each
method can run on its own Python version, and each method can use its
own virtual environment.  So if there is code that only runs on a
specific version of *pyTorch* for example, this is straightforward to
manage!


      


The plain text file ``methods.conf`` is used to restrict execution to
a defined set of methods and optionally to select python interpreters
independently for each method.  The contents typically looks like this

.. code-block::
   :caption: Example ``methods.conf`` file.

   # This is a comment
   import_data        tf212    # use the "tf212" interpreter / virtual environment
   train_network               # use the default interpreter
   
Interpreters must be defined in ``accelerator.conf`` (@@@).

NOTE: Methods are listed *without* the ``a_`` prefix and ``.py`` suffix in ``methods.conf``!

NOTE: Access restriction is disabled if ``auto-discover`` is enabled
for the directory in ``accelerator.conf`` (r@@).
