Buildscripts and Urd Database
=============================


Buildscripts are used to execute methods (@), pass data and
parameters, and collect resulting output.


How to find, name, and execute them
-----------------------------------

Buildscripts are stored along methods in method directories (@) and
are identified by filenames starting with the string "``build``".  The
"default" build script is named ``build.py`` and executed using ``ax
run``.  A build script named ``build_something.py`` is executed using
``ax run something``, and so on.

.. tip :: All available buildscripts can be listed along with
  descriptions using the ``ax script`` command.


Building Jobs
-------------

All build scripts contains a function called ``main()``, that provides
one object called ``urd``, like this

.. code-block::
   :caption: Minimal build script.

   def main(urd):
       # do something here...

A build script is typically used to build a number of jobs that may
pass data and results from one to the next.  Jobs are built using the
``urd.build()`` call.  The first argument to the call is the name of
the method (@) to be executed, and the remaining arguments are either
input parameters to the method or to the build process.


Here are some very simple examples

.. code-block::
    :caption: Build script running ``awesome_method`` with option ``x=3``.

    def main(urd):
        urd.build('awesome_method', x=3)

.. code-block::
    :caption: Pass reference to ``job1`` into ``next_method``.

    def main(urd):
        job1 = urd.build('awesome_method', x=3)
	job2 = urd.build('next_method', prev=job1)

.. code-block::
    :caption: Create a link to a file created by job1 to ``result_directory``.

    def main(urd):
        job = urd.build('awesome_method', x=3)
	job.link_result('outfile.txt')

In the last example, the resulting file created by the
``awesome_method`` job is considered to be of value for a human
observer and will therefore appear (as a soft link) in the ``result
directory`` (@@@).

The ``.build()`` function is just one of several class methods
provided by the ``urd`` object.  See the :ref:`Urd class documentation
<api:The Urd Class>` for full information.




Use JobList to find references to jobs
--------------------------------------

The ``urd`` input parameter from the ``main()``-function has a member
``joblist`` of type :ref:`JobList <api:The JobList Class>` that
collects references to and information about every built job inside a
build script.  It is used to find references to jobs build previously
in the script.

A specific job in a joblist can be found by searching for the
corresponding method using the joblist's ``.get()`` function, like
this

.. code-block::
    :caption: The last line uses ``urd.joblist.get()`` to locate a specific job using the method's name.

    def main(urd):
        urd.build('csvimport', data='file.txt')
        ...
        urd.build('dosomething', source=urd.joblist.get('csvimport')

The ``get()`` function will return the *last* job created based on the
input method (``csvimport`` in this case).  If there are several
builds based on this method, they cannot be uniquely identified using
this approach.  If this turns out to be a problem, one solution is to
assigning a unique *name* to each build, since the ``find()``-call can
also lookup methods based on the assigned names, like in this example:

.. code-block::
    :caption: Use ``urd.joblist.get()`` to locate a specific job using an assigned name.

    def main(urd):
        urd.build('csvimport', data='file1.txt', name='firstfile')
        urd.build('csvimport', data='file2.txt', name='otherfile')
        ...
        urd.build('dosomething', source=urd.joblist.get('firstfile')

.. tip :: ``get`` also takes a ``default`` argument that is returned
   if the search fails.

The joblist is actually a list, so it is also possible to get specific
indices in the list.

.. tip :: Accessing the last job in a list is a common pattern.  Use
    ``urd.joblist.get(-1)`` to achieve this.

In addition to ``get()`` that returns a job, the ``find()`` function
returns a new JobList of matching items.

See the :ref:`JobList <api:The JobList Class>` for full information.

Joblists are created and exists only while executing the build script,
but it is possible to make them persistent for future use and for
sharing jobs with others.  See next section on urd sessions and the
urd database for more information.



Urd Sessions and the Urd Database
---------------------------------

Joblists can be stored persistently in the Urd transaction database,
so references to anything from one particular job to all jobs ever
executed can be retrieved in a simple way.  In a transaction database,
information is always appended, it is never removed or changed, so a
complete history will always be available.

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
the urdlist must be the same for both ``begin()`` and ``finish()``.

.. note :: Nothing is stored in the database until ``urd.finish()`` is called.

.. note :: Urd sessions cannot be nested.


If the entry to be stored already exists in the database, meaning that
the key, timestamp, and contents is the same, exax accepts the input
silently but it does not store anything.  On the other hand, an
exception will be raised if the key and timestamp already exists, but
the contents is different.  This is a great way to verify that the
database contains the same thing as is produced by the current state
of the code base.



About timestamps
^^^^^^^^^^^^^^^^

The ``timestamp`` used to access items may be stated as either a
``date``, ``datetime``, ``int`` and tuples (``date``, ``int``),
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


Ending an Urd Session
^^^^^^^^^^^^^^^^^^^^^

There are three ways to end an urd session:

- execute the ``finish()`` call and have the session recorded/rejected/ignored. 

- end the build script “prematurely” without a ``finish()``-call. No
  data will be stored in Urd.

- issue an ``abort()`` call.  No data will be stored in Urd.

The abort() function is used like this

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

  - one that will record and associate the lookup with the ongoing
    session, and
    
  - one that will not.

Recording lookups is for transparency reasons, to make it clear which
jobs that are used as inputs to new jobs.  For example, the
``process`` session at ``2023-02-01`` is based on jobs in the
``import`` session with the same date.

The function calls that record the lookups are

  - ``get()``,
  - ``first()``, and
  - ``latest()``.

For any of these calls to work, they have to be issued from *within*
an ongoing session, i.e. after a ``begin()`` call. Otherwise Urd would
not be able to record session dependencies and an exception is raised.

The function calls that do not record anything are the

  - ``peek()``,
  - ``peek_first()``, and
  - ``peek_latest()``

calls, that in all other aspects are equivalent to the non-peek versions.
All these functions will be explained below.


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




