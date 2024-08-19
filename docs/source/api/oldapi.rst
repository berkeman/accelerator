

.. include:: currentjob.rst

The JobList Class
-----------------
.. _api-joblist:

The ``JobList`` class is inherited from the ``list`` class, and can
therefore be sliced etc.  The ``JobList`` itself is a reference to the
last job in the list.

.. autoclass:: accelerator.build.JobList
   :members:

.. _My target:



The Urd Class
-------------

The ``Urd`` class contains methods to build, record, and find jobs.

.. autoclass:: accelerator.build.Urd
   :members:
   :undoc-members:

The Job Class
-------------

The ``Job`` class is used in build scripts to get information about
and data from a completed job.

.. autoclass:: accelerator.Job
   :members:
   :undoc-members:


The CurrentJob Class
--------------------

The ``CurrentJob`` class is similar to the ``Job`` class, but used in
*running* jobs, typically something like this:

.. code-block::
    :caption: Make sure the build process is aware of the file.
	      
    def synthesis(job):
        data = ...
        with job.open('thefilename.txt', 'wt') as fh:
            fh.write(data)
   
or

.. code-block::
    :caption: Make sure the build process is aware of the file.
	      
    def synthesis(job):
        ...
	execute_some_external_program()
	job.register_file('output.bin')  # because we know it is created by the external program


Furthermore, it is possible to terminate execution of a method early,
like in this example that exits in prepare so that synthesis() is
never run:

.. code-block::
   :caption: Finish a job early

   def prepare(job)
       job.finish_eary()

   def synthesis():
       # This will never happen


Input filename takes a one or more arguments that will be joined
together with the ``input directory`` path, resulting in an absolute
path to a file in the input directory.  The following example creates
a filehandle to a file ``mysourcefile.txt`` in the ``input directory``:

.. code-block::
   :caption: input_filenane()

    def synthesis(job):
        fh = open(job.input_filename('mysourcefile.txt'))

The ``input directory`` is also available directly as

.. code-block::
   :caption: The path to ``input directory`` is also available.

   job.input_directory

But the ``input_filename()`` function is simpler to use.


	
.. autoclass:: accelerator.job.CurrentJob
   :members:
   :undoc-members:



The Colour Class
----------------

The colour class is used to provide colorful printout to capable
terminal emulators.  It is amazing.


.. autoclass:: accelerator.colourwrapper.Colour
   :members:



slask
-----

      
.. autoclass:: accelerator.extras.OptionEnum
   :members:
.. autoclass:: accelerator.extras.RequiredOption
   :members:
.. autoclass:: accelerator.extras.OptionDefault
   :members:

.. autoclass:: accelerator.extras.JobWithFile
   :members:
