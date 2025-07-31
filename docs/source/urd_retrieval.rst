Urd Database - Retrieval
========================

While the previous chapter introduced the Urd database and showed how
to *create* new entries. this chapter mainly describes how to
*retrieve* data.

The reason for retrieveing a session from the Urd database is that it
contains references to one or more jobs that contain some useful
information, typically some computed result.



Retrieving Sessions from the Database
-------------------------------------

A specific urd session can be retrieved from the Urd database using
the name of the *urdlist* and the *timestamp* it is associated with.

There are two sets of functions assigned for this, both will return
the requested urd session, and the difference is that

  - one that will `record and associate the lookup with the already
    ongoing urd session`, and

  - one that will not.

Recording a lookup means that the looked up urd session will be added
as a `dependency` to the ongoing urd session.  For example, a
*processing* session may look up some data stored in an *import*
session.  This makes dependencies between urd sessions transparent, so
it is clear how output from one job in one session is input to another
job in another session.



Retrieving a Session and make it a Dependency
---------------------------------------------

The ``urd`` object (that is input parameter to a build script's
``main`` function provides three function calls that record lookups:

  - ``get()`` ,
  - ``first()`` , and
  - ``latest()`` .


For any of these calls to work, they have to be issued from *within*
an ongoing manual urd session, i.e. after a ``begin()`` call but
before the corresponging ``finish()`` call.  If used elsewhere, Urd will
not be able to record session dependencies and an exception is raised.
Here is a working example.

.. code-block::
    :caption: The ``process`` urd session depends on the ``import`` session

    # then we retrieve and process it
    urd.begin('process', date)
    session = urd.latest('import')
    importjob = session.joblist.get('csvimport')
    urd.build('process_data', source=importjob)
    urd.finish('process')

The code above creates a new urd session called ``process``.  This
session retrieves the latest session from the ``import`` urdlist, and
takes the ``csvimport`` job (stored in the sessions joblist) as input
to the ``process_data`` method.

The contents of the Urd database can be viewed using the ``ax urd``
shell command:

.. code:: bash

    $ ax urd                              # 1
    alice/import
    alice/process

    $ ax urd import                       # 2
    timestamp: 2023-02-01
    caption  :
    deps     :
    JobList(
       [  0] csvimport : dev-2698
    )

    $ ax urd process/                     # 3
    2023-02-01
    2023-02-02

    $ ax urd process/2023-02-01           # 4
    timestamp: 2023-02-01
    caption  :
    deps     : alice/import/2023-02-01
    JobList(
       [  0] process_data : dev-2732
    )

At row ``#1``, the ``ax urd`` command is run without arguments.  It
returns the two *joblists* present in the database.

At row ``#2``, the command returns the *contents of the latest
session* in the ``import`` urdlist.  The joblist contains a
``csvimport`` job.

At row ``#3``, the command returns all urd sessions recorded in the
``process`` urdlist.  Each session is represented by its timestamp.

At row ``#4``, the session at timestamp 2023-02-1 of the *process*
urdlist reveals a joblist with a ``process`_data` job, but also a
``deps`` part where the ``alice/import/2023-02-01`` session is
mentioned.  This session holds the ``csvimport`` job that the
``process_data`` job used as input.  This urd session was created by
the example code above.

.. tip:: The Board web server is another convenient way to investigate
         the Urd database.


Retrieving a Session with no Dependency
---------------------------------------

The ``urd`` object function calls that do not record anything are

  - ``peek()``,
  - ``peek_first()``, and
  - ``peek_latest()``,

and they are in all other aspects equivalent to the non-peek versions.
These functions can be called anywhere in a build script, and not only
in an ongoing manual urd session.  For example

.. code-block::
    :caption: Using ``urd.peek_latest()`` anywhere

    session = urd.peek_latest('import')
    print('Latest import has timestamp', session.timestamp)



Description of the Retrieval Functions
--------------------------------------

- **Find the latest entries**, ``latest()`` and ``peek_latest()``:

  These calls are probably he most commonly used functions for session
  retrieval.  They will, for a given urdlist, return the session with
  most recent timestamp.  If there is no such session, an empty
  session is returned.  Empty sessions look like this

  .. code-block::

    {'deps': {}, 'joblist': JobList([]), 'caption': '', 'timestamp': '0'}

  The ``latest()`` function will record a dependency and must be
  issued in an ongoing manual urd session, i.e., between a set of
  ``begin()`` and ``finish()`` calls, while the ``peek_latest()``
  function can be called anywhere in a build script.


- **Finding an exact or closest match**:  ``get()`` or ``peek()``

  These functions will return the single session, if available,
  corresponding to a specified *urdlist* and *timestamp*, and is used
  like this

  .. code-block::

    urd.peek("test", "2018-01-01T23")

  The timestamp must match exactly for an item to be returned.  If
  there is no matching item, the call will return an empty session.

  **The strict matching behaviour can be relaxed** by prefixing the
  timestamp with one of ``<``, ``<=``, ``>``, or ``>=``.  For example

  .. code-block::

    urd.get("test", ">2018-01-01T01")

  may return an item recorded as "``2018-01-01T02``". Relaxed comparison
  is performed “from left to right”, meaning that

  .. code-block::

    urd.get("test", ">20")

  will match the first recorded session in a year starting with "``20``”, while

  .. code-block::

    urd.get("test", "<=2018-05")

  will match the latest timestamp starting with “``2018-05``” or less,
  such as “``2018-04-01``” or “``2018-05-31T23:59:59.999999``”.

  The ``get()`` call will record a dependency, while the ``peek()``
  call will not.


- **Find the first entries**, ``first()`` and ``peek_first()``:

  These calls will, for a given key, return the first session.  If
  there is no such session, an empty list is returned.

  The ``first()`` call will record a dependency, while the ``peek_first()``
  call will not.


Finding Recent Timestamps
-------------------------

The ``since()`` call is used to extract lists of timestamps
corresponding to recorded sessions. In its most basic form, it is
called with a timestamp like this

.. code-block::

    urd.since('test', '2016-10-05')

which returns a list with all existing timestamps in the ``test``
urdlist that are more recent than the provided argument.  It may for
example return

.. code-block::

   ['2016-10-06', '2016-10-07', '2016-10-08', '2016-10-09', '2016-10-09T20']

The ``since()`` call is rather relaxed with respect to the resolution
of the input. The input timestamp may be truncated *from the right*
down to only one digits. An input of zero is also valid.  For example,
all these are valid:

.. code-block::

    urd.since('test', '0')                    # returns all timestamps in the urdlist
    urd.since('test', '2016')
    urd.since('test', '2016-1')
    urd.since('test', '2016-10-05')
    urd.since('test', '2016-10-05T20')
    urd.since('test', '2016-10-05T20:00:00')

.. tip:: A common pattern is to do ``urd.since(something, 0)`` to get
   a list of all sessions in an urdlist.


@@@ ax job funkar direkt med urdlistor:  ax job :urdlist/timestamp:example_method



















Working with JobLists
---------------------

An urd session contains a joblist that holds all job ids associated
with the session.  This joblist object is of type ``JobList``, which
is an extension of the Python ``list`` class.  Traditional list
indexing and slicing works as expected, as shown in the example below

.. code::

   # find a joblist in an urd session
   session = urd.peek_latest('something')
   jl = session.joblist
   #
   print(jl[2])      # job id number 2 (start at 0)
   print(jl[3:5])    # a JobList containing jobs 3 and 4.

In addition the ``JobList`` class has a convenient ``get()`` function
that makes the joblist behave more like a dictionary.

.. code::

   jobid = jl.get('csvimport')

This will return the job id of the *last* ``csvimport`` job in the
joblist.  It returns ``None`` if there are no matches.  The ``get()``
function also works with list indices, like this example

.. code::

   # return last job id in joblist
   jobid = jl.get(-1)

that returns the last job id in the list.  Retrieving the last job id
in a list is a common pattern.  The advantage of using ``get(-1)``
instead of indexing ``[-1]`` is that the former will not fail if the
joblist is empty.

.. tip :: Accessing the last job in a list is a common pattern.  Use
    ``urd.joblist.get(-1)`` to achieve this.  The call returns
    ``None`` if the list is empty.

The ``get()`` function will return the job id of the *last* match.  If
there are several jobs of the same type, they can be found using the
``find()`` function that returns all matches in a joblist.
Information about this function and more is found in the JobList
documentation @@.
