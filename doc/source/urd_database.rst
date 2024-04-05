The Urd Database
================

The Urd database persistently stores references to all jobs built in
build scripts.  By default, references to *all jobs built in a build
script* will be stored automatically.  In addition, *a subsets of the
jobs* can be tagged and associated with a user defined name and
timestamp for easy retrieval.  The database is based on a transaction
log files, meaning that data can only be appended, never removed or
overwritten.

The exax server will automatically start a *local* urd server, which
is intended for personal use.  The urd server can also be set up in a
stand alone fashion, to share jobs and data between several users.


What is Stored in the Urd Database?
-----------------------------------

The Urd database stores *urd sessions*.  The main part of an urd
session is the *joblist*, which is basically a list of job ids
returned from ``build()``-calls when executing a build script.  When
the build script finishes, it creates a new urd session entry in the
database containing the joblist plus metadata.

Meta data in the urd session includes a timestamp, and it may also
contain references to other urd sessions, if there were any sessions
queried by the build script to find existing results or data to
use in the computations.


How Data is Stored in the Urd Database
--------------------------------------

The Urd database is basically a key-value storage, where the key is
composed of

  - a user name (will be set to ``$USER`` if omitted),
  - an arbitrary (descriptive) name, and
  - a timestamp, integer, or timestamp+integer tuple

A complete key could look like this: ``alice/import/2023-12-24``.  Here, ``alice`` is
the user, and the combination ``alice/import`` is called the
*urdlist*.  So the *urd session* is stored in the *urdlist*
``alice/import`` at timestamp ``2023-12-24``.

An example Urd database with six sessions, two users (``alice`` and
``bob``), and three urd lists may look like this

.. code::

  alice/imports/2024-01-08T19:30:00
  alice/imports/2024-01-09T19:30:00
  alice/imports/2024-01-10T19:30:00

  alice/process/2024-01-08T20:00:00

  bob/testing/7
  bob/testing/8
  bob/testing/9

Separation into urdlist and timestamps is motivated by common design
practice.  A particular user may work on several different parts of a
project, such as ``import``, ``process``, ``training``, ``validation``
etc.  Some of these parts may be run several times.  It could be every
time new data arrives (a new timestamp), or it could just be design
iterations (an integer).  Both timestamps and integers, as well as
tuples of both, are supported.


All Jobs are Automatically Stored in the Database
-------------------------------------------------

When a build script starts executing, the variable ``urd.joblist`` is
initiated to an empty state.  For each ``build()``-call in the script,
the job id of the corresponding job is then appended to the variable.
It does not matter if the job is actually built or just re-used
because it already exists.  The job id will be appended in either
case.

When the build script terminates, the contents of the ``urd.joblist``
variable is stored persistently in the Urd database under the key
``__auto__`` together with the timestamp when the execution started.

.. tip:: Use the shell command ``ax urd __auto__`` to see existing
   entries in the ``__auto__`` urdlist.

.. tip:: Use ``ax urd __auto__/<timestamp>`` to see the joblist at a
   specific timestamp.



Using Explicit Names and Timestamps
-----------------------------------

It is also possible to store partial sequences of this list of jobs
using user defined keys and timestamps.  The ``urd.begin()`` and
``urd.finish()`` calls are used for this purpose.  Here is an example:

.. code-block::
    :caption: An *urd session* is defined by ``begin()`` and
              ``finish()`` calls.

    def main(urd):
        urd.begin('testlist', '2023-06-20')
        job = urd.build('awesome_method', x=3)
	urd.finish('testlist')

The nomenclature is that the *urd session* is stored in the *urdlist*
``testlist`` with *timestamp* ``2023-06-20``.  In this case, the
session is a joblist with a single entry, a reference to the
``awesome_method`` job.

.. note:: An urdlist is always composed of two parts: user and a name,
   such as ``alice/import``.  If only one name is given, like
   ``import``, the user is implicit and the shell variable ``$USER``
   is used instead.

.. note:: The user part is very convenient when several programmers
          work in the same project, or in projects when "virtual"
          users are added for the sake of separation.


Collisions and Updates
----------------------

Data is always appended to the Urd database.  Existing data cannot be
erased or changed.  It is, however, possible to have a later entry
replace an earlier one, but this situation has to be stated
explicitly.  These are the rules that applies

 - It is always possible to store a new session using an existing key
   and a timestamp that is more recent than the latest existing one.

 - If the name and timestamp already exists, execution will stop and
   an error will be raised if the contents of the urdlist is
   *different* from what is already stored.

 - If name, timestamp, and contents are *the same*, nothing will be
   stored in the database and execution will just move on.  This is
   very useful for verification, for example to make sure that the
   current version of the source code corresponds to the jobs on disk.

   (Detta borde utvecklas.)

 - A new entry can replace an old one by specifying ``update=True`` in
   the ``build()``-call, like this example

   .. code-block::

     def main(urd):
       urd.begin('testlist', '2023-06-20', update=True)
       ...


 - Entries newer than a specific timestamp can be for ever ignored
   using ``urd.truncate(timestamp)``.  Specifically, setting timetamp
   to "0" will make the database to appear completely empty. (Although
   all entries are still available in the plain text transaction log
   file.)

The server serves requests one at a time, so there are no races
possible when the Urd database is serving multiple users.


The JobList
-----------
  This section deals with
the features of the ``joblist`` itself.

Any job in ``joblist`` can be found easily.  For example, a specific
job in a joblist can be found by searching for the corresponding
method using the joblist's ``.get()`` function, like this

.. code-block::
    :caption: The last line uses ``urd.joblist.get()`` to locate a specific job using the method's name.

    def main(urd):
        urd.build('csvimport', data='file.txt')
        ...
        urd.build('dosomething', source=urd.joblist.get('csvimport')

The ``get()`` function will return the *last* job created based on
method name (``csvimport`` in this case).  If there are several builds
based on the same method, they cannot be uniquely identified using
this approach.  If this turns out to be a problem, one solution is to
assigning a unique *name* to each build, since the ``get()``-call can
also lookup methods based on the assigned names, like in this example:

.. code-block::
    :caption: Use ``urd.joblist.get()`` to locate a specific job using an assigned name.

    def main(urd):
        urd.build('csvimport', data='file1.txt', name='firstimport')
        urd.build('csvimport', data='file2.txt', name='otherimport')
        ...
        urd.build('dosomething', source=urd.joblist.get('firstimport')

.. tip :: ``get`` also takes a ``default`` argument that is returned
   if the search fails.

The joblist is actually a list, so it is also possible to get specific
indices in the list.

.. tip :: Accessing the last job in a list is a common pattern.  Use
    ``urd.joblist.get(-1)`` to achieve this.

In addition to ``urd.joblist.get()`` that returns a single job, the
``urd.joblist.find()`` function returns a new JobList of matching
items.  See the :ref:`JobList <api:The JobList Class>` for full
information.






The Urd Database in more detail
-------------------------------


.. note :: The name of the urdlist must be the same for both
           ``begin()`` and ``finish()`` and cannot be omitted.

.. note :: After a ``urd.begin()``-call, nothing is committed to the
   database until ``urd.finish()`` is called.

.. note :: If no ``begin()`` and ``finish()`` calls are used, the
            default behaviour of a build script is to store the
            contents of ``urd.joblist`` in the Urd database using the
            key ``_auto`` together with the current timestamp.

.. note :: Urd sessions cannot be nested.


If the entry to be stored already exists in the database, meaning that
the key, timestamp, `and` contents is the same, Exax accepts the input
silently but it does not store anything.  On the other hand, an
exception will be raised if the key and timestamp already exists, but
the contents is different.  This is a straightforward way to verify
that the database contains the same thing as is produced by the
current state of the code base.




The Urd
database is the topic of the next section.

@@@@ The JobList api doc does not show the .get-function at all!!!!!!!!!


Urd Sessions and the Urd Database
---------------------------------

A major feature of Exax is that joblists can be stored `persistently`
and `searchable`, and this has turned out to be extremely useful for
future use and for sharing jobs with others.

The data is stored in the Urd transaction database, so references to
anything from one particular job to all jobs ever executed can be
retrieved in a simple way.  In the transaction database, information
is always appended, and never removed or changed, so a complete
history will always be available.

.. tip :: Entries in the urd database can be explored using the ``ax urd`` command.

Storing a joblist persistently is done by encapsulating the build
calls to be stored between ``urd.begin()`` and ``urd.finish()`` calls,
like in the following example:

.. code-block::
    :caption: An *urd session* is defined by ``begin`` and ``finish`` calls.

    def main(urd):
        urd.begin('testlist', '2023-06-20')
        job = urd.build('awesome_method', x=3)
	urd.finish('testlist')

The nomenclature is that the *session* has been stored in the
*urdlist* ``testlist`` with *timestamp* ``2023-06-20``.  The name of
the urdlist must be the same for both ``begin()`` and ``finish()`` and
cannot be omitted.

.. note :: Nothing is stored in the database until ``urd.finish()`` is called.

.. note :: If no ``begin()`` and ``finish()`` calls are used, the
            default behaviour of a build script is to store the
            contents of ``urd.joblist`` persistently in the Urd
            database using the key ``_auto`` together with the current
            timestamp.

.. note :: Urd sessions cannot be nested.


If the entry to be stored already exists in the database, meaning that
the key, timestamp, `and` contents is the same, Exax accepts the input
silently but it does not store anything.  On the other hand, an
exception will be raised if the key and timestamp already exists, but
the contents is different.  This is a straightforward way to verify
that the database contains the same thing as is produced by the
current state of the code base.



About the key
^^^^^^^^^^^^^


About timestamps
^^^^^^^^^^^^^^^^

The ``timestamp`` used to access items may be stated as either a
``date``, ``datetime``, ``int`` , (``date``, ``int``),
(``datetime``, ``int``) or ``"datetime+int"``, where dates and
datetimes may be specified using strings in format

``"%Y-%m-%d %H:%M:%S.%f"``

(See Python’s ``datetime`` module for explanation.)

A specific timestamp can be shortened than the above specification in
order to represent a wider time range. The following examples cover
all possible cases::

  '2016-10-25'                 # day resolution
  '2016-10-25 15'              # hour resolution
  '2016-10-25 15:25'           # minute resolution
  '2016-10-25 15:25:00'        # second resolution
  '2016-10-25 15:25:00.123456' # microsecond resolution

  '2016-10-25+3'               # Example of timestamp + int

Note that
  - ``ints`` without ``datetimes`` sort first,
  - ``datetimes`` without ``ints`` sorts before ``datetimes`` with ``ints``,
  - shorter ``datetime`` strings sorts before longer ``datetime`` strings, and
  - a timestamp must be > 0.


Truncating Urd Lists
^^^^^^^^^^^^^^^^^^^^

Data can never be erased from the urd database, but a *restart marker*
can be inserted at any time giving the appearance of that everything
after the marker timestamp is removed, like in this example:

.. code-block::
    :caption: Urd session with restart marker.

    def main(urd):
	urd.truncate('testlist', '2023')
        ...

The above ``truncate`` call makes all entries in ``testlist`` that
are from 2023 or later inaccessible.

.. tip ::  Truncating to zero gives the appearance of a completely empty urdlist.


.. note :: Data is never erased in the Urd transaction database.
   Furthermore, all data is stored in an easily readable format, so if
   data is believed to be "lost", it is possible to find by looking in
   the database files.


Overwriting the Last session
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Although data cannot be erased or changed in the urd database, it is
possible to *replace* the last entry by a new one.  Both the old and
new entry will be stored in the database, but only the latter will be
visible.  This example shows how to do it:

.. code-block::
    :caption: Replace last urd entry.

    def main(urd):
        urd.begin('testlist', '2023-06-20', update=True)
	...

@@@ är det bara senaste som kan uppdateras, eller är det alla?


Ending an Urd Session
^^^^^^^^^^^^^^^^^^^^^

There are three ways to end an urd session:

- execute the ``urd.finish()`` call and have the session recorded/rejected/ignored. 

- end the build script “prematurely” without a ``urd.finish()``-call. No
  data will be stored in Urd.

- issue an ``urd.abort()`` call.  No data will be stored in Urd.

The ``abort()`` function is used like this

.. code-block::
   :caption: Abort an Urd Session (nothing is stored in the Urd database).

   urd.begin('test')
   urd.abort()
   # execution continues here, a new session can be initiated
   urd.begin('newtest')

A new urd session can be initiated once the previous is finished or aborted.



Finding and listing existing sessions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A specific urd session, i.e. a joblist with some meta information, can
be retrieved from the Urd database using its *key* (@@@
key=name=path?)  and *timestamp*.  There are two sets of functions
assigned for this

  - one that will `record and associate the lookup with the ongoing
    session`, and
    
  - one that will not.

Recording lookups is for transparency reasons, to make it clear which
jobs from which joblists that are used as inputs to new jobs.
Consider the following example:

.. code-block::
    :caption: The ``process`` urd session depends on the ``import`` session

    date = '2023-02-01'
    # import something
    urd.begin('import', date)
    urd.build('csvimport', filename='data.csv')
    urd.finish('import')

    # process it
    urd.begin('process', date)
    session = urd.get('import', date)
    importjob = session.urdlist.get(-1)
    urd.build('process', importjob=importjob)
    urd.finish('process')

The ``urd.get()`` call happens, and must happen, inside an ongoing urd
session, i.e. between ``begin()`` and ``finish()``.  The result from
the call will therefore be stored in the ``process``-session, so that
it will be apparent from examining the ``process`` session which
``import`` session that it depends on.


The function calls that record the lookups are

  - ``get()``,
  - ``first()``, and
  - ``latest()``.

For any of these calls to work, they have to be issued from *within*
an ongoing session, i.e. after a ``begin()`` call. Otherwise Urd will
not be able to record session dependencies and an exception is raised.

The function calls that do not record anything are the

  - ``peek()``,
  - ``peek_first()``, and
  - ``peek_latest()``

calls, that in all other aspects are equivalent to the non-peek versions.
All these functions will be explained below:


- Finding an exact or closest match:  ``get()`` or ``peek()``

  These functions will return the single session, if available,
  corresponding to a specified *list* and *timestamp*, see the following
  example

  .. code-block::

    urd.begin('anotherlist')
    urd.get("test", "2018-01-01T23")

  The timestamp must match exactly for an item to be
  returned.

  If there is no matching item, the call will return an empty session,
  i.e. something like this

  .. code-block::

    {'deps': {}, 'joblist': JobList([]), 'caption': '', 'timestamp': '0'}

  The strict matching behaviour can be relaxed by prefixing the
  timestamp with one of “<”, “<=”, “>”, or “>=”.  For example

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


- Find the latest entries, ``latest()`` and ``peek_latest()``:

  These calls will, for a given key, return the session with most
  recent timestamp.  If there is no such session, an empty list is
  returned (@@ is this correct?)

  
- Find the first entries, ``first()`` and ``peek_first()``:

  These calls will, for a given key, return the first session.  If
  there is no such session, an empty list is returned (@@ is this
  correct?)


Listing all timestamps After a Specific Timestamp
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``since()`` call is used to extract lists of timestamps
corresponding to recorded sessions. In its most basic form, it is
called with a timestamp like this

.. code-block::
   
    urd.since('test', '2016-10-05')
    
which returns a list with all existing timestamps in the ``test`` urd
list more recent than the one provided, such as for example

.. code-block::

   ['2016-10-06', '2016-10-07', '2016-10-08', '2016-10-09', '2016-10-09T20']

The ``since()`` call is rather relaxed with respect to the resolution
of the input. The input timestamp may be truncated *from the right*
down to only one digits. An input of zero is also valid.  For example,
all these are valid:

.. code-block::

    urd.since('test', '0')
    urd.since('test', '2016')
    urd.since('test', '2016-1')
    urd.since('test', '2016-10-05')
    urd.since('test', '2016-10-05T20')        # @@@ är det T eller space?
    urd.since('test', '2016-10-05T20:00:00')




