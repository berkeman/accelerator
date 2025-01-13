
@ behöver text som säger att all input skall ligga i input_directory	


@@ loading and saving sliced files måste beskrivas någonstans.


The CurrentJob Class
--------------------

The ``CurrentJob`` class is similar to (and inherits) the ``Job``
class, and is used in *running* jobs (while the ``Job`` class is used
with completed jobs.)  An object of type ``CurrentJob`` is provided as
an optional input argument named "``job``" to ``prepare()``,
``analysis()``, and ``synthesis()``.

.. note:: Most class methods from the ``Job`` class available to
   ``CurrentJob`` too. (@) This chapter only covers the parts unique
   to ``CurrentJob``.

-----

.. autoclass:: accelerator.job.CurrentJob
   :members:
   :undoc-members:
   :exclude-members: input_directory
-----

Below are some more details and examples.



Create a dataset: ``datasetwriter()``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
@@@



Abort the method: ``finish_early()``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is possible to terminate execution of a method early, like in this
example that exits in prepare so that synthesis() is never run:

.. code-block::
   :caption: Finish a job early

   def prepare(job)
       job.finish_eary()

   def synthesis():
       # This will never happen

It is however very unlikely that there is a need to do this.



Read input files: ``input_filename()`` and ``open input()``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

These functions help accessing files stored in the ``input directory``
(defined in the configuration file. @@)

``input_filename()`` takes a one or more arguments that will be joined
together with the ``input directory`` path, resulting in an absolute
path to a file in the input directory.  The following example creates
a filehandle to a file ``mysourcefile.txt`` in the ``input
directory``:

.. code-block::
   :caption: input_filenane()

    def synthesis(job):
        fh = open(job.input_filename('mysourcefile.txt'), 'rt')

Finally, ``open_input()`` is a wrapper around the traditional
``open()``-function that opens files relative to the ``input
directory``.  Note that it is not possible open files for *writing*
with this function.



Save data: ``save()``, ``open()``, and ``json_save()``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Data can be saved using the
  - ``save()`` (for Pickle),
  - ``json_save`` (for JSON), and
  - ``open()`` (for general file) functions.

Using these functions will ensure that Exax is aware of the files that
are created, so that they can be tracked and easily found later.

.. code-block::
    :caption: Make sure the build process is aware of the file.

    def synthesis(job):
        data = ...
        with job.open('thefilename.txt', 'wt') as fh:
            fh.write(data)

Filnames on disk will be exactly as specified.



``register_file()``
^^^^^^^^^^^^^^^^^^^

If an external program called by the method generates a file as part
of its execution, it can be added manually using the
``register_file()`` function like this

.. code-block::
    :caption: Make sure the build process is aware of the file.

    def synthesis(job):
        ...
        execute_some_external_program()
        job.register_file('output.bin')  # because we know it is created by the external program


@@ compare/see method_exec for more info.






