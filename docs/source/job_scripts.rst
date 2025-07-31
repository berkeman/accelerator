Job scripts
===========


Job scripts are the main workhorses in an exax project.  Most
computations are carried out in there, and if the project is
partitioned into several job scripts, only those affected by code
changes will have to be re-built when re-executing the project's build
script.


Building Job Scripts
--------------------

Job scripts are built using a ``build()`` call, either from a *build
script* like this

.. code-block::
   :caption: Building ``my_script`` from a build script.

   def main(urd):
       job = urd.build('my_script', x=3)

or from *another job script* (as a "*subjob*") like this

.. code-block::
   :caption: Building ``my_script`` from another job script.

   from accelerator.subjobs import build

   def synthesis():
       job = build('my_script', x=4)

Unlike build scripts, job scripts are not executable from the command
line.


Existing Jobs Will be Re-Used Whenever Possible
-----------------------------------------------

The first thing that happens in the build-call is that the job
script's source code and input parameters are compared to what already
exists in the project workdirs.  Then, one out of two things will
happen

  1. The combination of source code and input parameters has not been
     seen before, and therefore the job script is *built* and a new
     *job directory* is created.  When execution finishes, the return
     value from the build call is a *Job object* containing references
     to the new *job*.

  2. A matching *job directory* already exists, and the build
     call **immediately** returns a *Job object* containing references
     to the existing *job*.

The job directory will contain all input and output relating to the
build, and also meta information about the execution itself.  Here is
a more or less complete list of what is saved

- the job scripts's source code
- input parameters
- build timestamp
- profiling information
- Python version
- exax version
- job id of the builder
- input directory
- method package
- any other files the job "depends extra" on

(The build script has additional support functionality, such as
JobLists (@), the Urd database (@), and result linking (@), to aid
development, whereas building a subjob has less decorations.)



Passing Input Parameters
------------------------

There are *three kinds* of input paramters to a job script: *options*,
*datasets*, and *jobs*.  They are all declared early in the job script's
source file, see the following example

.. code-block::
   :caption:  Example of all three types of input parameters speficied in a job script.

   options = dict(
                 x=3,
                 name='protomolecule',
                 f = float,
             )
   datasets = ('source_dataset', 'anothersourceds',)
   jobs = ('previous_job',)

.. note:: ``datasets`` and ``jobs`` are *tuples*, and therefore it is *key
  to remember to add a comma* after any single item like the
  ``jobs=('previous_job'',)`` assignment above.  Otherwise it will be
  interpreted as a string or characters, and things will break.

- The ``options`` parameter is a dictionary, that can take almost
  "anything", with or without default values and type definitions.

- The ``datasets`` parameter is a list or tuple of datasets references.

- The ``jobs`` parameter is similar to ``datasets``, but contains a
  list of job references.

Parameters are assigned by the build call like this:

.. code-block::
   :caption: Assigning input parameters to a build.

   urd.build('my_script',
         x=37,
         name='thename',
         f=42.0
         source=ds,
         previous=job0
   )

.. note:: In the example above, all parameters have unique names, so
          it is not necessary to specify if, say, ``x`` is an option,
          a dataset, or a job.

          If names are not unique, it is possible to explicitly state
          the kind of parameter using ``..., datasets={'source': ds},...`` and so on.



Receiving Input Parameters
--------------------------

Inside the method, parameters are available like in the following example

.. code-block::
   :caption: Print some input parameters to stdout.

   options={'x': 37, 'name': 'myname',}
   datasets=('ds',)
   jobs=('previous',)
 
   def synthesis():
       print(options.x, options.name)
       print(datasets.ds.columns)
       print(jobs.previous)

In a running job script, all three parameter types are converted to
the ``accelerator.DotDict`` type, which is basically a Python ``dict``
supporting dot-notation for accessing its values.

.. tip :: Input parameters members can be accessed using dot notation,
          like ``options.x`` etc.


Options: Default Values and Typing
----------------------------------

If an option is defined with a *value* (such as
``options=dict(x=37)``), this value is also the default value that
will be used if none is assigned by the build call.  The default value
also affects the typing.  A default value of 37 will not match a
string, for example, but it will match a float.

If instead the option is specified using a *type*, (such as
``options=dict(f=float)``), the input parameter must be of the same type.
If the input parameter is left unspecified in this case, the (default)
value will be ``None``.

.. note::
   - If a default value is set, this value will be used if left unassigned.

   - A default value also specifies the allowed set of types of the input.

   - If the default value is a type, this is the only allowed type.

   - If the default value is a type and left unassigned, its value will become ``None``.



Execution and Data Flow
-----------------------

There are three functions used for code execution in a method, of
which at least one is mandatory.  They are, listed in execution order

 - ``prepare()``
 - ``analysis()``
 - ``synthesis()``

The functions will be described below in reverse order, starting with
``synthesis()``, since this is the simplest and most commonly used for
more basic job scripts.



``synthesis()``
...............

The ``synthesis()`` function is executed as a single process, and its
return value is stored persistently as the job's output value, like
shown in this example:

.. code-block::
  :caption: This is job script ``a_test.py``...

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

The ``analysis()`` function is intended for parallel processing.  When
run, it is forked into a number of parallel processes, called
*slices*.  The number of slices is fixed and specified in the
configuration file:

.. code-block::
   :caption: Part of ``accelerator.conf`` specifying number of parallel processes.

   slices: 64

This can be set to any number at project initialisation, and it is
then the same fixed number for the whole project.  The ``ax init``
command will by default initiate this to the number of available cores
on the machine.  (It makes little sense to set it to a larger number,
but in some cases a lower number is preferred in order to limit the
max load on the machine.)

The number of slices, as well as the current fork number *sliceno*
(ranging from zero to *slices* minus one) are available as parameters to
the ``analysis()`` function

.. code-block::
    :caption: Example of ``analysis()`` function.

    def analysis(sliceno, slices):
        print('This is slice %d/%d' % (sliceno, slices))
        return sliceno * sliceno

When all forks have completed execution, the return value from all
``analysis()`` calls become available to the ``synthesis()`` function
(described earlier) as the ``analysis_res`` input parameter.
``analysis_res`` is an iterator, containing one element per analysis
process.  It also has a convenient class method for merging all
results together, like this

.. code-block::
    :caption: Use of ``analysis_res`` and its automagic result merger ``merge_auto()``.

    def synthesis(analysis_res):
        x = analysis_res.merge_auto()

``merge_auto()`` typically does what is expected, but is of course not
mandatory to use.  In the example above, the returned integers from
``analysis()`` will be added together into one number.  It will merge
sets or dictionaries, update Counters, etc.



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
``job`` object that contains a set of useful job-related helper
functions.

Return values from ``prepare()`` and ``analysis()`` are stored
*temporarily* in the job directory by default, and removed upon job
completion.  In contrast, the return value from ``synthesis()`` is
stored *persistently* and considered to be the default output from the
job.



Share Data using Return Value
-----------------------------

The simplest way to share data between a job script and another job or
build script is to use the return value.

In a job script that creates some data that should be available
elsewhere, just return it:

.. code-block::
    :caption: Example of return value.

    def synthesis():
        data = ...
        return data

Then this data is available in a build script like this

.. code-block::
    :caption: Return value from job script into a build script.

    def main(urd):
        job = urd.build('scriptreturningdata')
        data = job.load()

Similarly, to access the data in another job script

.. code-block::
    :caption: Return value from one job script to another.

    jobs=('jobreturningdata',)
    def synthesis():
        data = jobs.jobreturningdata.load()

assuming it was provided by the build script

.. code-block::
    :caption: Corresponding build script passing the first job as input to the second.

    def main(urd):
        job = urd.build('scriptreturningdata')
        urd.build('scriptusingdata', jobreturningdata=job)

Note how simple this is, and without the need to make up arbitrary filenames.
Instead of filename, the job script (i.e. source code and input parameters)
is used to find the correct data file.

.. tip:: In many cases, return values can often be used instead of
   explicitly creating any files.


Writing Files
-------------

Any file written by a job is stored in the current job directory.
This is also where the source code and input parameters to the current
build are stored. Keeping everything at one place ensures that the
relationship between input, source code, and output is always clear.

.. note :: Files created by a job are and *should always be stored in
  the corresponding job directory*.  By default, the current working
  directory is set to the current job directory when the job script is
  executing to simplify this.  Avoiding filenames with absolute paths
  will ensure that the files end up the current job directory.

Files can be created by any means, but it is encouraged to use the
built-in helper functions that among other things will create files in
the correct location.  These functions will also *register* the files,
which is the topic of the next section.

The first helper finction is ``job.save()``.  This stores data as a
Python pickle file:

.. code-block::
   :caption: Writing a pickle file.

   def synthesis(job):
       data = ...
       job.save(data, 'thisisthenameofapicklefile')

There is also a dedicated function for writing json files:

.. code-block::
   :caption: Writing a json file.

   def synthesis(job):
       data = ...
       job.json_save(data, 'andthisisajsonfile')

In addition, there is a generic ``job.open()`` function as well, that
is a wrapper around Python's ``open()`` function:

.. code-block::
   :caption: Use of ``job.open()``.

   def synthesis(job):
       data = ...
       with job.open('thefilename', 'wt') as fh:
           fh.write(data)

.. note :: Reading and writing files in ``analysis()`` is special,
  because this function is running as several parallel processes.  For
  this reason, it is possible to work with *sliced files*, simply
  meaning that one "filename" in the program corresponds to a set of
  files on disk, one for each process.

  This is handled using ``save(..., sliceno=sliceno)``, see @.

In addition, it is possible to create *temporary files* that only
exists during the execution of the method and will be automatically
deleted upon job completion.  This *might* be useful for huge
temporary files if disk space is a major concern.  Add the parameter
``temp=True`` to ``job.save()`` or ``job.json_save()`` to make the file
temporary.



Registering Files
-----------------

*Registering* a file means making exax aware of it, so that simple
helper functions can list and retrieve the data directly from a job
object.  For example, registered files can be listed using
``job.files()``, and accessed using ``job.open()`` or
``job.json_load()``.  Registered files are also trivially added to the
exax Board web server for visual inspection.


Almost all created files are *registered automatically by default*
when the method finishes execution.  Files in subdirectories is the
exception, they are not automatically registered.

.. note :: Files in subdirectories are not registered automatically.

Files can also be registered manually.  Manual registration does,
however, turn off automatic registration for all files.  Registration
is either manual or automatic.

.. note :: If a file is manually registered, automatic registration is
   disabled for all other files, so they have to be registered
   manually too, if needed.


Calls to ``job.save()``, ``job.json_save()``, and ``job.open()`` will
register the created file, *and* turn off automatic registration of
all other files.  This is a reasonable default.

To register a file manually, use ``job.register_file()``, for example
like this, when the file has been created by an external command:

.. code-block::
   :caption:  Register a file created by external program.

   def synthesis(job):
       # use external program ffmpeg to generate a movie file "out.mp4"
       subprocess.run(['ffmpeg', ..., 'out.mp4'])
       job.register_file('out.mp4')

Several files could be registered at once using glob patterns, like this

.. code-block::
   :caption: Registering a file using ``job.register_files()``

   def synthesis(job):
       # create file "myfile1.txt", "myfile2.txt", ..., "myfile10.txt"
       job.register_files("myfile*.txt")

.. note:: The call ``job.register_files()`` will return a set containing the names of all files that were registered!

*Temporary files are not registered*, even though they are created by
the helper functions.  On the other hand, if a temporary file is being
registered manually, it stops being temporary.




Find and Load Created Files 
----------------------------

Files in a job are easily accessible by other methods and build
scripts, see this example where data created in a job is read back
into the running build script.  The example assumes the files are
registered, but this is not a requirement.

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

There is also a ``job.json_load()`` function to directly load json
content.  Note that exax has no idea what if it is json or pickle or
something else.  Make sure to use the proper functions.

The names of a job's all registered files are available using
``job.files()``.  This call will return a set of all filenames in the
job.  The absolute path of a particular file can be retrieved using
the ``job.filename()`` function, like this

.. code-block::
   :caption: Find files created by a job.

    def main(urd):
        job = urd.build('my_script', ...)
        print(job.files())
        print(job.filename('myfile'))

.. note :: There is no need to use absolute paths with exax.  Absolute
  paths should in fact be avoided, since they prevent moving things
  around in the file system later.

  But it is nice to know that it is very easy to find any file
  generated in an exax project.

.. tip ::
   Files can also be listed and viewed in *exax Board* using a web browser.

.. tip ::
   The ``ax job`` shell command can also list and view files in a job.



Reading Input Files
-------------------

Input data files should ideally be stored in the ``input directory``
specified in the configuration file.  If so, input files could be
addressed using a relative path, and therefore be moved around in the
file system without causing any changes to the project code.

There are three helper functions for input data:

.. code-block::
   :caption: reading input files

   # Returns the path to the input directory.
   job.input_directory()

   # Returns the full path to a specific file in the input directory.
   # Multiple arguments will be fed to Python's os.path.join()
   job.input_filename('thefile')
   job.input_filename('or', 'a', 'path', 'to', 'thefile')

   # Opens a file in the input directory for reading.
   # (This is a wrapper around Python's open() function.)
   fh = job.open_input('thefile', 'rb')


.. tip ::
  Use the ``input_directory`` and corresponding helper
  functions to avoid having absolute paths in your project code!



Descriptions
------------

A text description is added to a job script using the ``description``
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
shown when typing ``ax method`` to list all job scripts and their
short descriptions.  A detailed description may follow on consecutive
lines, and it will be shown when doing ``ax method <a particular
method>``.



Retrieving stdout and stderr
----------------------------

Everything written to ``stdout`` and ``stderr`` (using for example
plain ``print()``-statements) is always stored persistently in the job
directory.  It can be retreived using the ``ax job`` command, for
example like this

.. code-block:: sh
   :caption: ``ax job`` print stdout and stderr

    ax job test-43 -O

It is also straightforward to view the output in *Board*.

In a job or build script, this output is accessible using the
``job.output()`` function.



Progress/status reporting
-------------------------

If a job takes a long time to complete, pressing CTRL+T will force
exax to print a message on stdout.  This message can be tailored to
the running program in the following way

.. code-block:: python
   :caption: custom status messages (show when pressing CTRL-T)

   from accelerator import status

   def synthesis():
       msg = "my status message: %s"
       with status(msg % ('init',) as update:
           for task in tasklist:
	       update(msg % (task,))

In this example, the status message will update for each new task in
the tasklist.  The output message will automatically add execution
time, if it is running in prepare, analysis, or synthesis, and when in
analysis also provide information about which slice the the message
belongs to.  It may for example look like this

.. code-block:: text

 589443 STATUS:      analysis(2) (9.0 seconds)
 589443 STATUS:         my status message: task_number_one

or

.. code-block:: text

  589443 STATUS:      synthesis (14.1 seconds)
  589443 STATUS:         my status message: the_synthesis_run

.. tip::

   Exax Dataset iterators (@@@ ref) use status reporting to tell which Dataset
   in a Dataset chain it is currently working on.



Subjobs
-------

Job scripts are typically built by build scripts, but in a similar way
job scripts can be built by other job scripts.  There is no difference
from a built job's perspective, but the nomenclature is that when a
job script is building a job it is called a *subjob*.

Subjobs are built in the ``synthesis()`` function like this

.. code-block::
   :caption: Building a job from within a job.

   from accelerator.subjobs import build

   def synthesis():
       job = build('my_script')

The ``subjobs.build()`` call uses the same input parameters and syntax
as the ``urd.build()`` call in a build scripts.  Similarly, the
returned ``job`` object is an instance of the ``Job`` class (@) that
contains some useful helper functionality.

.. note :: Subjobs are *not* visible in build scripts and do not show
   up in ``urd.joblist``!  Furthermore, they are not recorded in the
   urd database.

Subjobs are registered in the post-data of a job and can be retrieved by
inspecting ``job.post.subjobs``.



Subjobs and Datasets
....................

Datasets created by subjobs can be made available to the job that
built the subjob, to make it look like the dataset was created there.
It works as shown in the following example

.. code-block::
   :caption: Link a subjob's dataset to the current job.

   from accelerator import subjobs

   def synthesis():
       job = subjobs.build('create_a_dataset')
       ds = job.dataset(<name>)
       ds = ds.link_to_here(name=<anothername>)

In the example above, the job script ``create_a_dataset`` creates a
dataset.  A reference to this dataset is created using the
``job.dataset()`` function.  Finally, using the ``ds.link_to_here()``
function, a soft link is created in the current job directory,
pointing to the job directory of the subjob, completing the illusion
that the dataset is created by the current job script.

Similarly, it is possible to override the dataset's ``previous``, like so

.. code-block::
   :caption: Override a subjob's dataset's previous

    ...
    ds = ds.link_to_here(name=<anothername>, override_previous=<some dataset>)

The ``ds_link_to_here()`` function returns a reference to the "new"
linked dataset.
