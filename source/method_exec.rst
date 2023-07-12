Methods - Writing and Executing
===============================

All source code in a project is separated into one or more files
called methods.

This chapter describes how to write and work with methods, and how to
save and share computed results.  For information about file naming
and directories, see chapter :doc:`method`.


Building Methods
----------------

First a note on nomenclature: A *method* is a small program (with
extra features).  A method is said to be *built* when executed, and in
the build process a persistent *job* is created.

When the method starts building, one of the first things that happens
is that a new *job directory* (@) is created and the current working
directory (cwd) will point into it.  The job directory will contain
all input and output relating to the build, including parameters,
source code, python version, any output generated, and so on.

If the job already exists, meaning that a method with the same name,
source code, and input parameters has be built in the past, exax will
immediately return a reference to that job instead of building it
again.

Methods can be built either by build scripts (@) or by methods as
subjobs (@).  In a build script, it may look like this

.. code-block::
   :caption: Building ``mymethod`` from a build script.

   def main(urd):
       job = urd.build('mymethod', x=3)

and similarly in a method

.. code-block::
   :caption: Building ``mymethod`` from another method.

   from accelerator.subjobs import build

   def synthesis():
       job = build('mymethod', x=4)

The build script has significant support, such as JobLists (@), the
Urd database (@), and result linking (@), to aid development, whereas
building a subjob has much less decorations.



Passing Input Parameters
------------------------

There are three kinds of input paramters to a method, and they are all
declared early in the source:

.. code-block::
   :caption: Example of the three types of input parameters

   options = dict(
                 x=3,
                 stuff={
                     'a': 4,
                     'name': 'protomolecule',
                     'z'=float,
             })
   datasets = ('source', ['inputs'],)
   jobs = ('previous',)

.. note:: ``datasets`` and ``jobs`` are *tuples*, and therefore it is *key
  to remember to add a comma* after any single item like the
  ``jobs=('previous',)`` assignment above.  Otherwise it will be
  interpreted as a string or characters, and things will break.

- The ``options`` parameter is a dictionary, that can take almost
  "anything", with or without default values and type definitions.

- The ``datasets`` parameter is a list or tuple of datasets.  Note the
  "``['inputs']``" above that specifies a list of input datasets with
  the name "``input``".

- The ``jobs`` parameter is similar to ``datasets``, but contains a list
  of named jobs.

The parameters are set by the build call like this:

.. code-block::
   :caption: Assigning input parameters to a build.

   build('method',
         x=37,
         stuff=dict(name='thename', z=4.2),
         source=ds,
         inputs=[ds1, ds2, ds3],
         previous=job0
   )

.. note:: The parameter names are by default assumed to be unique, so
  that all parameters can be listed without explicitly telling if it is
  a dataset, job, or option.

  It is possible to explicitly state the
  kind using ``..., datasets={'source': ds},...`` and so on.

Inside the method, parameters are available like in the following example

.. code-block::
   :caption: Print some input parameters to stdout.

   def synthesis():
       print(options.x, options.stuff['name'])   # @@ dotdict?
       print(datasets.inputs[0])
       print(jobs.previous)


See manual on formal option-rules for more info (flera sidor...)@@



Execution and Data Flow
-----------------------

There are three functions used for code execution in a method, of
which at least one is mandatory.  They are, listed in execution order

 - ``prepare()``
 - ``analysis()``
 - ``synthesis()``

The functions will be described below in reverse order, starting with
``synthesis()``.


- ``synthesis`` is executed as a single process, and its return value is
  stored persistently as the job's output value, like shown in this example:

  .. code-block::
    :caption: This is method ``a_test.py``...

    options = dict(x=3)
    def synthesis()
        val = options.x * 2
        return dict(value=val, caption="this is a test")

  .. tip :: The ``options`` object is of type ``DotDict`` (ref@), and
            its members can therefore be accessed using dot notation, like ``options.x`` etc.


  When the job has completed execution, the return value is conveniently
  available using the returned object's ``load()`` function, like this

  .. code-block::
    :caption: ...and a corresponding build script ``build_mytest.py`` to build it.

    def main(urd):
        job = urd.build('test', x=10)
        data = job.load()
        print(data['value'])

  If this is executed using ``ax run mytest``, the build script will
  execute the method ``test`` and print the value "20" to standard
  output.


- ``analysis()`` is forked into several processes and used for
  parallel processing applications.  This is particularly useful
  together with exax's ``Dataset`` described here (@).  The number of
  forks is statically specified in the configuration file (@), and
  optionally available as the ``slices`` input parameter.  The forks
  are numbered from zero to ``slices-1`` and the number of the current
  fork is available as the ``sliceno`` parameter:

  .. code-block::
      :caption: Example of ``analysis()`` function.

      def analysis(sliceno, slices):
          print('This is slice %d/%d' % (sliceno, slices))
          return sliceno * sliceno

  The return value from ``analysis()`` is available to the
  ``synthesis()`` function as the ``analysis_res`` input parameter.
  ``analysis_res`` is an iterator, containing one element per analysis
  process.  It also has a convenient class method for merging all
  results together, like this

  .. code-block::
      :caption: Use of ``analysis_res`` and its automagic result merger ``merge_auto()``.

      def synthesis(analysis_res):
          x = analysis_res.merge_auto()

  ``merge_auto()`` typically does what is expected.  In the example
  above, the returned integers from ``analysis()`` will be added
  together into one number.  It will merge sets or dictionaries, and
  it will update Counters, etc.


- ``prepare()`` is executed first, and just like ``synthesis()`` it
  runs as a single process.  The main reason for ``prepare()`` is to
  make it possible to set up datastructures and datasets prior to
  parallel processing in the ``analysis()`` function.  If no parallel
  processing is required, it is encouraged to use ``synthesis()``
  instead of ``prepare()``.

  The return value from ``prepare()`` is available to both
  ``analysis()`` and ``synthesis()`` as ``prepare_res``, like this

  .. code-block::
      :caption: ``prepare_res`` example

      def prepare(job):
          dw = job.datasetwriter()
          dw.add('index', 'number')
          return dw

      def analysis(sliceno, prepare_res):
          dw = prepare_res
          or ix in range(10):
              dw.write(ix)

Return values from ``prepare()`` and ``analysis()`` are just stored
temporarily in the job directory by default, and removed upon job
completion.  In contrast, the return value from ``synthesis()`` is
stored persistently and considered to be the default output from the
job.



Input Parameters to ``synthesis()`` etc.
----------------------------------------

As shown in the previous section, ``analysis_res`` is available to
``synthesis()``, and ``prepare_res`` is available to both
``analysis()`` and ``synthesis()``.

In addition. ``analysis()`` has access to the ``sliceno`` and ``slices`` parameters.

And all three functions have access to ``job``, which is an instance
of ``CurrentJob`` (@), that contains convenience functions for saving
files etc, see next section and the class documentation here (@).



Writing Files
-------------

A method can create any number of files while executing.  By making
exax aware of these files, they can be associated with the jobs
creating them, so that results can be connected to code creating it
without the need for specific filenames.  This has a number of advantages and is discussed more in (@).

.. note :: Files created by a job are and should always be stored in
  the corresponding job directory.  By default, the current working
  directory is set to the current job directory when the method is
  executing to simplify this.

.. tip :: The "``result directory``" should be the place to find files
  that are considered to be relevant "output" from a project run.  Soft
  links in the result directory link to files in jobs using the
  ``job.link_result()`` function (@).

There are built-in helper functions for creating files in the correct
location and at the same time ensuring that exax is aware of their
existence.  Here's a simple example of how a file is created by a
method (using the ``save()`` function) and then accessed in the build
script that created the job.

.. code-block::
   :caption: Writing and reading files (see  currentjob@ ref for info about ``save()`` and more.

    # in the method "methodthatsavefiles"
    def synthesis(job):
        data1 = ...
	job.save(data1, 'afilename')
	job.save(data2, 'anotherfilename')

    # in the build script
    def main(urd):
        job = urd.build('methodthatsavefiles')
        data = {}
        for fn in job.files:
            data[fn] = job.load(fn)

The ``save()`` function uses Python's Pickle module to serialise data.
There is also a ``json_save()`` function, and a general ``open()``
function with full flexibility, see ref @.

.. note :: Reading and writing files in ``analysis()`` is special, because this
  function is running as several parallel processes.  For this reason,
  it is possible to work with *sliced files*, simply meaning that one
  "filename" in the program corresponds to a set of files on disk, one
  for each process.

  This is handled using ``save(..., sliceno=sliceno)``, see @.

In addition, it is possible to create temporary files, that only
exists during the execution of the method and will be automatically
deleted upon job completion.  The only reason for temporary files is
if disk space is a concern.



Keeping Track of created files
------------------------------

Any file written by a job will be stored in the current job directory,
so that the relation to input, source code, and output is always
clear.  It turns out that it is advantageous if exax is aware of
created files.

.. tip ::  Files can be listed and viewed in *exax Board* using a web browser.

  The ``ax job`` command can list and view files in a job.

  In a build script, ``job.files`` lists all files in a job.

The ``save()`` and ``json_save()`` functions (@ref) create connections
between files and the jobs creating them automatically.  When more
flexibility is required, there is a wrapper around the ``open()``
function available in the ``job`` input parameter that is used much
like the ordinary ``load()``-function.  Consider this

.. code-block::
   :caption: Use job.load() to have Exax aware about any created files.

    def synthesis(job):
        data = ...
        with job.open('myfile', 'wt') as fh:  # job.open() is wrapper around open()
	    fh.write(data)

The file `myfile` is now visible in *Board*, using the ``ax job``
function, and in a build script like this

.. code-block::
   :caption: Find files created by a job.

    def main(urd):
        job = urd.build('mymethod', ...)
	print(job.files())
	print(job.filename('myfile'))

The first print will show all files created by the job as a ``set``.
The second will show the full absolute path to the file ``myfile``.

.. note :: There is no need to use absolute paths with exax.  Absolute
  path should be avoided, since they depend on the file system of the
  particular machine being used.  But it is nice to know that it is
  very easy to find any file generated in an exax project.

Sometimes, a method may call an external program that is generating
files as part of the execution.  Exax can be made aware of these files
using the ``register_file()`` function.

.. code-block::
   :caption:  Register a file created by external program.

   def synthesis(job):
       # use external program ffmpeg to generate a movie file "out.mp4"
       subprocess.run(['ffmpeg', ..., 'out.mp4'])
       job.register_file('out.mp4')



Descriptions
------------

It is possible to add a text describing what a method is doing using
the ``description`` variable.  This description is available in *exax
Board* (@) and using the ``ax method`` (@) command, and it looks like
this

.. code-block::
    :caption: Example of description

    description="""Collect movie ratings.

    Movie ratings are collected using a parallel interation
    over all...
    """

.. tip :: Use ``ax method`` or *exax Board* to see descriptions of all
   available methods.

If the description is multi-lined, the first row is a short
description that will be shown when typing ``ax method`` to list all
methods and their short descriptions.  A detailed description may
follow on consecutive lines, and it will be shown when doing ``ax
method <a particular method>``.  Exax updates its record of
descriptions when re-scanning the method directories.



Storing stdout and stderr
-------------------------

Everything written to ``stdout`` and ``stderr`` (using for example
plain ``print()``-statements) is always stored persistently in the job
directory.  It can be retreived using the ``ax job`` command, for
example like this

.. code-block:: sh
   :caption: ``ax job`` print stdout and stderr

    ax job test-43 -O

It is also straightforward to view the output in *Board*.

In a program, the output is accessible using the ``job.output()``
function (@, skriv om hur accessa out, err, analysis, ...).



------------------

description (``ax method``)
      
create them

enable in configfile


functions

parameters

internal return values
merge_auto

exit return values

job object, job.open

what is in the job directory:
 + profiling
 + list of all files, subjobs, ...


Subjobs
-------

