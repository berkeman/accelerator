Methods
=======


Methods are the main workhorses in an exax project.  Most computations
are carried out there, and if the project is partitioned into several
methods, only those affected by code changes will have to be re-built
when re-executing the project's build script.


Building Methods
----------------

Methods are built using a ``build()`` call, either from a *build
script* like this

.. code-block::
   :caption: Building ``mymethod`` from a build script.

   def main(urd):
       job = urd.build('mymethod', x=3)

or from *another method* (as a *subjob*) like this

.. code-block::
   :caption: Building ``mymethod`` from another method.

   from accelerator.subjobs import build

   def synthesis():
       job = build('mymethod', x=4)


Existing Jobs Will be Re-Used Whenever Possible
-----------------------------------------------

The first thing that happens in the build-call is that the method's
source code and input parameters are compared to what already exists
in the project's workdirs.  Then, one out of two things will happen

  1. The method is *built*, i.e. executed, and a new *job directory*
     is created.  When execution finished, the return value from the
     build call is a *job object* containing references to the *job*.

  2. A matching *job directory* already exists, and the build
     call **immediately** returns a *job object* containing references
     to the existing *job*.

The job directory will contain all input and output relating to the
build, and also meta information about the execution itself.  Here is
a more or less complete list of what is saved

- the method's source code
- input parameters
- build timestamp
- profiling information
- Python version
- exax version
- job id of the builder
- input directory
- method package

The build script has significant support, such as JobLists (@), the
Urd database (@), and result linking (@), to aid development, whereas
building a subjob has less decorations.



Passing Input Parameters
------------------------

There are *three kinds* of input paramters to a method: *options*,
*datasets*, and *jobs*.  They are all declared early in the method's
source file, see the following example

.. code-block::
   :caption:  Example of all three types of input parameters speficied in a method.

   options = dict(
                 x=3,
                 name='protomolecule',
                 f = float,
             )
   datasets = ('source', 'anothersource',)
   jobs = ('previous',)

.. note:: ``datasets`` and ``jobs`` are *tuples*, and therefore it is *key
  to remember to add a comma* after any single item like the
  ``jobs=('previous',)`` assignment above.  Otherwise it will be
  interpreted as a string or characters, and things will break.

- The ``options`` parameter is a dictionary, that can take almost
  "anything", with or without default values and type definitions.

- The ``datasets`` parameter is a list or tuple of datasets.

- The ``jobs`` parameter is similar to ``datasets``, but contains a
  list of named jobs.

The parameters are set by the build call like this:

.. code-block::
   :caption: Assigning input parameters to a build.

   build('method',
         x=37,
         name='thename',
         f=42.0
         source=ds,
         previous=job0
   )

.. note:: In the example above, all parameters have unique names, so
          it is not necessary to specify if, say, ``x`` is an option,
          dataset, or job.

          It is possible to explicitly state the
          kind using ``..., datasets={'source': ds},...`` and so on.



Receiving Input Parameters
--------------------------

Inside the method, parameters are available like in the following example

.. code-block::
   :caption: Print some input parameters to stdout.

   def synthesis():
       print(options.x, options.name)
       print(datasets.ds.columns)
       print(jobs.previous)

Inside the running method, all three parameters are converted to
``accelerator.DotDict``, which are like ordinary Python dictionaries, but also
supporting the dot-notation for accessing its values.

.. tip :: The ``options`` object is of type ``accelerator.DotDict``
          (ref@), and its members can therefore be accessed using dot
          notation, like ``options.x`` etc.


Options: Default Values and Typing
----------------------------------

If an option is defined with a *value* (such as ``x=3`` above), this
value is also the default value that will be used if not assigned by
the build call.  The default value also affects the typing.  A default
value of 37 will not match a string, for example, but it will match a
float.

If instead the option is specified using a *type*, (such as
``f=float`` above), the input parameter must be of the same type.  If
the input parameter is left unspecified in this case, the value will
be ``None``.




Execution and Data Flow
-----------------------

There are three functions used for code execution in a method, of
which at least one is mandatory.  They are, listed in execution order

 - ``prepare()``
 - ``analysis()``
 - ``synthesis()``

The functions will be described below in reverse order, starting with
``synthesis()``.



``synthesis()``
...............

The ``synthesis()`` function is executed as a single process, and its
return value is stored persistently as the job's output value, like
shown in this example:

.. code-block::
  :caption: This is method ``a_test.py``...

  options = dict(x=3)
  def synthesis()
      val = options.x * 2
      return dict(value=val, caption="this is a test")



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



``analysis()``
..............

The ``analysis()`` function is intended for parallel processing.  It
is forked into a number of parallel processes, specified in the
configuration file

.. code-block::
   :caption: Part of ``accelerator.conf`` specifying number of parallel processes.

   slices: 64

This number must be the same for the whole project, and can be set to
any number.  The ``ax init`` command will by default initiate this to
the number of available cores on the machine.  (It makes little sense
to set it to a larger number.)

The number of slices, as well as the current fork number (ranging from
zero to slices minus one) are available as parameters to the
``analysis()`` function

.. code-block::
    :caption: Example of ``analysis()`` function.

    def analysis(sliceno, slices):
        print('This is slice %d/%d' % (sliceno, slices))
        return sliceno * sliceno

The return value from all ``analysis()`` calls are available to the
``synthesis()`` function (described earlier) as the ``analysis_res``
input parameter.  ``analysis_res`` is an iterator, containing one
element per analysis process.  It also has a convenient class method
for merging all results together, like this

.. code-block::
    :caption: Use of ``analysis_res`` and its automagic result merger ``merge_auto()``.

    def synthesis(analysis_res):
        x = analysis_res.merge_auto()

``merge_auto()`` typically does what is expected.  In the example
above, the returned integers from ``analysis()`` will be added
together into one number.  It will merge sets or dictionaries, update
Counters, etc.



``prepare()``
.............

The ``prepare()`` function, if present, is executed first, and just
like ``synthesis()`` it runs in a single process.  The main reason for
``prepare()`` is to simplify any preparation work like setting up
datastructures and datasets prior to parallel processing in the
``analysis()`` function.  If no parallel processing is required, it is
encouraged to use just ``synthesis()`` instead of ``prepare()``.

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
        for ix in range(10):
            dw.write(ix)




Function Inputs and Outputs
...........................

As shown in the previous section,
  - ``analysis_res`` is available to ``synthesis()``, and
  - ``prepare_res`` is available to both ``analysis()`` and ``synthesis()``.

In addition, ``analysis()`` has access to the ``sliceno`` and
``slices`` parameters, and all three functions have access to the
``job`` object that will be described shortly.

Return values from ``prepare()`` and ``analysis()`` are stored
*temporarily* in the job directory by default, and removed upon job
completion.  In contrast, the return value from ``synthesis()`` is
stored *persistently* and considered to be the default output from the
job.




Writing and Registering Files
-----------------------------

Any file written by a job is stored in the current job directory, so
that the relationship between input, source code, and output is always
clear.

*Registering* a file means making exax aware of it, so that simple
helper functions can list and retrieve the data directly from a job
object.

.. note :: Files created by a job are and *should always be stored in
  the corresponding job directory*.  By default, the current working
  directory is set to the current job directory when the method is
  executing to simplify this.  Avoiding a filename without absolute
  path will ensure that the file ends up the current job directory.

The default behaviour is the expected one. Files are typically created
using Pythons ``open()`` function.  All created files will be
automatically _registered_ by exax when the execution of the method
finishes.  The registration will make the files visible and easy
accessible from the corresponding job object.




  
All files created in a job will be added to the job's meta
information, so that files can be listed and opened directly from a
job object, as is the topic of the next section.

Sometimes, it is convenient to not have exax keep track of the created
files.  This could be for example if the files are not at all relevant
outside the job.

# @@@ Hur undvika att registrera den enda filen som skapats av en annan exekutabel?

# @@@ we call it "registered files"
# @@@ files in subdirectories are not registered
# @@@ all files created (except temporary files) will be registered by default
# @@@ using any of register_file, register_files, or job.open will change behavour to only explicit registering
# @@@ register_file on a temp file will un-temp the file
# @@@ register_files() can take wildcards
# @@@ register_files() returnerar ett set med filnamn den registerat






  There are built-in helper functions for creating files in the correct
location and at the same time ensuring that exax is aware of their
existence.  The simplest way is to use ``job.open()`` instead of
``open()``, like this

.. code-block::
   :caption: Use of ``job.open()`` to register a file to the current job

   def synthesis(job):
       data = ...
       with job.open('thefilename', 'wt') as fh:
           fh.write(data)

There are also dedicated functions to write Python pickle and json
files, like this

.. code-block::
   :caption: writing pickle and json files

   def synthesis(job):
       data = ...
       job.save(data, 'thisisapicklefile')
       job.json_save(data, 'andthisisajsonfile')

Sometimes, a method may call an external program that is generating
files as part of the execution.  Exax can be made aware of these files
using the ``register_file()`` function.

.. code-block::
   :caption:  Register a file created by external program.

   def synthesis(job):
       # use external program ffmpeg to generate a movie file "out.mp4"
       subprocess.run(['ffmpeg', ..., 'out.mp4'])
       job.register_file('out.mp4')


.. note :: Reading and writing files in ``analysis()`` is special,
  because this function is running as several parallel processes.  For
  this reason, it is possible to work with *sliced files*, simply
  meaning that one "filename" in the program corresponds to a set of
  files on disk, one for each process.

  This is handled using ``save(..., sliceno=sliceno)``, see @.

In addition, it is possible to create temporary files, that only
exists during the execution of the method and will be automatically
deleted upon job completion.  This *might* be useful for huge
temporary files if disk space is a major concern.



Find and Load Created Files 
----------------------------

Files in a job are easily accessible by other methods and build
scripts, see this example where data in a job is read back into the
running build script.

.. code-block::
   :caption: Writing and reading files (see  currentjob@ ref for info about ``save()`` and more.

    # in the method "a_methodthatsavefiles.py"
    def synthesis(job):
        ...
	job.save(data1, 'afilename')
	job.save(data2, 'anotherfilename')

    # in the build script "build.py"
    def main(urd):
        job = urd.build('methodthatsavefiles')
        data = {}
        for filename in job.files:
            data[filename] = job.load(filename)

All filenames are available using ``job.files()``, that returns a set
of all filenames in the job.  The absolute path of a particular file
can be retrieved using the ``job.filename()`` function, like this

.. code-block::
   :caption: Find files created by a job.

    def main(urd):
        job = urd.build('mymethod', ...)
	print(job.files())
	print(job.filename('myfile'))

.. note :: There is no need to use absolute paths with exax.  Absolute
  paths should in fact be avoided, since they prevent moving things
  around in the file system later.

  But it is nice to know that it is very easy to find any file
  generated in an exax project.

.. tip ::
   Files can also be listed and viewed in *exax Board* using a web browser.

   The ``ax job`` shell command can also list and view files in a job.



Descriptions
------------

A text description is added to a method using the ``description``
variable.  This description is visible in *exax Board* (@) and using
the ``ax method`` (@) command, and it looks like this

.. code-block::
    :caption: Example of description

    description="""Collect movie ratings.

    Movie ratings are collected using a parallel interation
    over all...
    """

.. tip :: Use ``ax method`` or *exax Board* to see descriptions of all
   available methods.

Descriptions work much like git commit messages.  If the description
is multi-lined, the first row is a short description that will be
shown when typing ``ax method`` to list all methods and their short
descriptions.  A detailed description may follow on consecutive lines,
and it will be shown when doing ``ax method <a particular method>``.
Exax updates its record of descriptions when re-scanning the method
directories.



Retrieving stdout and stderr
-------------------------

Everything written to ``stdout`` and ``stderr`` (using for example
plain ``print()``-statements) is always stored persistently in the job
directory.  It can be retreived using the ``ax job`` command, for
example like this

.. code-block:: sh
   :caption: ``ax job`` print stdout and stderr

    ax job test-43 -O

It is also straightforward to view the output in *Board*.

In a method or build script, this output is accessible using the
``job.output()`` function.



Subjobs
-------

Job are typically built by build scripts, but in a similar way jobs
can be built by methods as well.  There is no difference from a built
jobs perspective, but the nomenclature is that when a method is
building a job it is called a *subjob*.

Subjobs are built in the ``synthesis()`` function like this

.. code-block::
   :caption: Building a job from within a job.

   from accelerator.subjobs import build

   def synthesis():
       job = build('mymethod')

The ``subjobs.build()`` call uses the same input parameters and syntax
as the ``urd.build()`` call in a build scripts.  Similarly, the
returned ``job`` object is an instance of the ``Job`` class (@) that
contains some useful helper functionality.

.. note :: Subjobs are *not* visible in build script and do not show
   up in ``urd.joblist``!  Furthermore, they are not recorded in the
   urd database.

Subjobs are registered in the post-data of a job and can be retrieved by
inspecting ``job.post.subjobs``.



Subjobs and Datasets
....................

Datasets created by subjobs can be made available to the job that
built the subjob, to make it look like the dataset was created there.
It works as show in the following example

.. code-block::
   :caption: Link a subjob's dataset to the current job.

   from accelerator import subjobs

   def synthesis():
       job = subjobs.build('create_a_dataset')
       ds = job.dataset(<name>)
       ds = ds.link_to_here(name=<anothername>)

In the example above, the method ``create_a_dataset`` creates a
dataset.  A reference to this dataset is created using the
``job.dataset()`` function.  Finally, using the ``ds.link_to_here()``
function, a soft link is created in the current job directory,
pointing to the job directory of the subjob, completing the illusion
that the dataset is created by the current method.

Similarly, it is possible to override the dataset's ``previous``, like so

.. code-block::
   :caption: Override a subjob's dataset's previous

    ...
    ds = ds.link_to_here(name=<anothername>, override_previous=<some dataset>)

The ``ds_link_to_here()`` function returns a reference to the "new"
linked dataset.
