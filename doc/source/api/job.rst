
@ beskriva att Job() kan användas för att ta en jobid-sträng till ett jobobjekt

The Job Class
-------------

The ``Job`` class is used in build scripts and methods to get
information about and data from a *completed job*.  Note that there is
also a ``CurrentJob`` class which inherits the ``Job`` class and is
used for file writing and job control *during execution* of a job.

-----

.. autoclass:: accelerator.Job
   :members:
   :undoc-members:
   :exclude-members: version,number,workdir

-----



What is stored in the job - ``files()``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use ``job.files()`` to get a set of all files created by and stored in
the job.  It can also take a *glob*-pattern like this

.. code-block::
   :caption: list all files in a job ending with "``.jpg``"

    print(job.files("*.jpg"))

Similarly, use ``job.datasets`` to get a ``Datasetlist`` (@) of all
datasets created by and (at least partially) stored in the job.

.. code-block::
   :caption: List all datasets in a job

    print(job.datasets)



Accessing Files - ``load()``, ``json_load()``, and ``open()``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Files in a job can be accessed directly using the
  - ``job.load()`` (for Pickle),
  - ``job.json_load()`` (for JSON), and
  - ``job.open()`` (for any kind of file).

.. code-block::
   :caption: Get the contents of files stored in a job.

    job = urd.build('something')
    # load the contents of the file named "result.picke",
    # where return value from synthesis() is stored
    data1 = job.load()
    # load the contents from another (json) file in the job
    data2 = job.json_load("thefilename")
    with job.open("anotherfile", "rb") as fh:
        data3 = fh.load()

It is also possible to get the absolute path to a file in a job is
using the ``job.filename()`` function, like this

.. code-block::
   :caption: Find absolute path to a file in a job.

    print(job.filename("thefilename"))



Accessing Datasets - ``datasets()``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In a fashion similar to files, datasets in a job can be retrieved
using ``job.dataset()`` like this

.. code-block::
   :caption: Get a ``Dataset`` object from a job.

    job.dataset('mydataset')

Without argument the function fetches the ``default`` dataset, which
is a common thing to do.



Job Meta Information - ``input_directory()``, ``input_filename()``, ``method``, ``path``, ``params``, ``post``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- The ``job.input_directory()`` function returns the full absolute path to
  the input directory.

  .. code-block::
   :caption: The path to ``input directory`` is also available.

   job.input_directory

  But the ``input_filename()`` function is simpler to use and should be
  prefered when accessing files stored in job directories.

- The name of the method is stored in ``job.method``.

- The absolute path of the job directory is stored in ``job.path``

- The dictionaries ``job.params`` and ``job.post`` contain a lot of
  information.  In this context the most relevant thing is that
  ``job.param`` is a dictionary containing all input parameters to the
  job, i.e. the ``options``, ``datasets``, and ``jobs`` parameters.
  Additional data stored here includes execution times, filenames,
  datasets, subjobs, python interpreter version, git commit, and so on.

And them there are a few more meta properties that are not documented
here.  Have a look at the source code for full coverage.



Stdout and Stderr - ``output()``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Everything that the method has written to ``stdout`` and ``stderr`` is
also stored in the job directory.  This data is accessed using
``job.output()``, like this

.. code-block::
   :caption: Accessing data written to stdout and stderr of a job.

    job = urd.build('thejob', ...)
    print(job.output()              # everything
    print(job.output('synthesis'))  # only synthesis
    print(job.output('analysis'))   # opny analysis
    print(job.output('prepare'))    # only prepare
    print(job.output(5))            # only analysis slice 5
    print(job.output('parts'))      # everything stored in a DotDict()



Link to Result Directory - ``link_result()``
^^^^^^^^^^^^^^^^^^^^^^^^

A soft link from a file in a job directory to the result directory is
created using ``job.link_result()``:

.. code-block::
   :caption: Make a soft link in ``result directory`` pointing to file in job.

    job = urd.build('thejob', ...)
    job.link_result('data1.txt')
    job.link_result('datax.txt', 'data2.txt')  # rename link destination

This will result in two links in the result directory: `data1.txt`
linking to a file with the same name in the job directory, and
`data2.txt`, linking to the file `datax.txt` in the job directory.



Reference to speficic file - ``withfile()``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``job.withfile()`` will return a ``JobWithFile`` object specifying
a particular file in a particular job.  This is used to feed specific
files from a job into another job, like this

.. code-block::
   :caption: Example of ``JobWithFile`` useage

    def main(urd):
        job1 = urd.build('filemaker')
	job2 = urd.build('fileuser', infile=job1.withfile('theintendedfile'))

The point is that the second job in the example above does not need to
know about any filename.  The first job maybe creates hundreds of
files, and the second job must know which one of them it should use.
The ``withfile`` solves this without explicitly passing a filename to
the ``fileuser`` method.  See more here on ``JobWithFile`` (@)



Chained jobs - ``chain()``
^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``job.chain()`` is similar to ``Dataset.chain()``, but perhaps not
used as extensively.  See explanation here @.
