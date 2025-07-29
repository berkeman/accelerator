Urd Database - Introduction
===========================

So far in this documentation, it has been shown how jobs (including
computed results) can be retrieved immediately by executing the
corresponding job script.  In a way, this is a database lookup from
source code and parameters to computed results.

While this is very convenient when running smaller projects and doing
development work, it is not ideal for larger scale operations.  There
is a need to fetch computations and results based on something simpler
and human readable, like a string and a timestamp.  This is,
basically, what the Urd database does.

The Urd database persistently stores references to all jobs built in
build scripts.  References to *all* built jobs are always stored by
default, and in addition, *a subset of the jobs* can be tagged and
associated with a user defined name and timestamp for easy retrieval.

The database is based on transaction log files.  From a user's
perspective, information can appear to be removed or modified, but the
transaction log files that actually store the data are always appended
to, never modified.  So even if the user "erases everything", all
information is still available in the human readable log files.

The exax server automatically starts a *local* urd server, for the
sake of convenience and personal use.  The urd server can also be set
up in a stand alone fashion, to share jobs and data between several
users.



What is Stored in the Urd Database?
-----------------------------------

The Urd database stores *urd sessions*.  The main part of an urd
session is the *joblist*, which is basically a list of job ids
returned from ``build()``-calls when executing the whole or a part of
a build script.  When a session is complete, it is stored as a new
single entry in the database that includes the joblist and metadata.

Urd session meta data includes a timestamp, and it may also contain
references to other urd sessions, if there were any sessions queried
by the build script to fetch existing results or data to use in the
computations.  In this fashion, *dependencies* between different
sessions can be tracked and made observable.

Here's an example of what an urd session may look like, when generated
using the ``ax urd`` command:

.. code:: text

   :caption: An urd session as output from "ax urd ab/trainer/latest"

   timestamp: 2025-07-28T13:37:00
   build job: dev-75
   caption  :
   deps     :
   JobList(
      [  0]     train_model    : dev-76
      [  1]     validate_model : dev-77
   )


   
How is Data Stored?
-------------------

The Urd database is basically a key-value store, where the key is
composed of

  - a user name (will be set to ``$USER`` if omitted),
  - an arbitrary (descriptive) name, and
  - a timestamp, integer, or timestamp+integer tuple

A complete key could look like this: ``alice/import/2023-12-24``.
Here, ``alice`` is the user, and the combination ``alice/import`` is
called an *urdlist*, which can hold many entries, each having an
unique timestamp.  So the key above points to the *urd session* stored
in the *urdlist* ``alice/import`` at *timestamp* ``2023-12-24``.

An example Urd database with six sessions, two users (``alice`` and
``bob``), and three urd lists may look like this

.. code:: text

  :caption: examples of urdlist-timestamp keys
	  
  # different time resolution
  alice/imports/2024-01-10
  alice/imports/2024-01-09T19
  alice/imports/2024-01-08T19:30:00

  # use an integer instead of timestamp
  bob/testing/7
  bob/testing/8
  bob/testing/9

  # use a timestamp-integer tuple
  alice/process/2024-01-08+3

Separation into urdlist and timestamps is motivated by common design
practice.  A particular user may work on several different parts of a
project, such as ``import``, ``process``, ``training``, ``validation``
etc.  Some of these parts may be run several times.  It could be every
time new data arrives (a new timestamp), or it could just be design
iterations (an integer).  Both timestamps and integers, as well as
tuples of both, are supported.



The Automatic Urd List
----------------------

When a build script starts executing, the internal variable
``urd.joblist`` is initiated to an empty list.  For each
``build()``-call in the script, the job id of the corresponding job
gets appended to this variable.  It does not matter if the job is
actually built or just re-used because it already exists.  The job id
will be appended in either case.

When the build scrip terminates, the contents of the ``urd.joblist``
variable is stored persistently in the Urd database under the key
``__auto__`` together with the timestamp when the execution started.

.. tip:: Use the shell command ``ax urd __auto__/`` (with a slash) to
   see existing entry timestamps in the ``__auto__`` urdlist.

.. tip:: Use ``ax urd __auto__/<timestamp>`` to see the joblist at a
   specific timestamp.

   Or just ``ax urd __auto__`` to see the latest entry.

Since the automatic Urd list stores all build-calls performed by any
build script, it can be used to recall any previous build call by
timestamp.



Initiating a manual Urd session
-------------------------------

The ``__auto__`` urdlist stores all executions, but it is a bit hard
to use.  Therefore it is possible to tailor urdlists for specific use.

It is possible store just partial sequences of job ids to urdlists
with used defined key names and timestamps.  The ``urd.begin()`` and
``urd.finish()`` calls are used for this purpose.  Here is an example:

.. code-block::
    :caption: An *urd session* is defined by ``begin()`` and
              ``finish()`` calls.

    def main(urd):
        urd.begin('testlist', '2023-06-20')
        job = urd.build('awesome_script', x=3)
	urd.finish('testlist')

The nomenclature is that the *urd session* is stored in the *urdlist*
``testlist`` with *timestamp* ``2023-06-20``.  The session in this
case will contain a joblist with just a single entry, a reference to
the ``awesome_script`` job.

Note how the *user* part of the urdlist is omitted in the example
above, only a descriptive name is being used.  If the user part is
implicit, like in this case, the value of the shell variable ``$USER``
is used.

The example also specifies the name of the urdlist twice, in both the
``begin()`` and ``finish()`` functions.  This is a requirement and
safety measure to prevent unnecessary writes to the wrong urdlist.  If
the names differ, execution will stop and raise an error.


.. note:: An urdlist is always composed of two parts: user and a name,
   such as ``alice/import``.  If only one name is given, like
   ``import``, the user is implicit and the shell variable ``$USER``
   is used instead.

.. note:: The name specified in the ``begin()`` and ``finish()``
          functions *must be the same*.

.. note:: Urd sessions cannot be nested.  A second ``begin()`` without
          a ``finish()`` call inbetween will cause a failure.

.. note:: The timestamp must be specified once, in *either* the
          ``begin()`` or ``finish()`` call.  Sometimes the timestamp
          is known at execution start, sometimes only when it ends.
	  
.. tip:: The user part of the urdlist name is convenient to use when
          several programmers work in the same project.  It also
          enables the use of "virtual" users for the sake of
          separation.  There could be for example a ``test`` user, a
          ``production`` user and so on.


@@@ alla urd-shell-kommandon
@@@ med tilde och tak osv
@@@ hur timestamp-förkortningar fungerar



Ending a Manual Urd Session
---------------------------

There are three ways to end an urd session:

- Execute the ``urd.finish()`` call.  One of three things will happen: *store*, *ignore*, or *fail*.  See next section for more information.
  
- end the build script “prematurely” without a
  ``urd.finish()``-call. No data will be stored in Urd.

- issue an ``urd.abort()`` call.  No data will be stored in Urd.

The ``abort()`` function is used like this

.. code-block::
   :caption: Abort an Urd Session (nothing is stored in the Urd database).

   urd.begin('test')
   urd.abort()
   # execution continues here, a new session can be initiated
   urd.begin('newtest')

A new urd session can only be initiated once the previous is finished
or aborted.  Only one urd session can be active at a time.  (Apart
from the ``__auto__`` session, which is always there in the
backgroud.)



Collisions and Updates
----------------------

Since Urd is a transactional database, it will never overwrite
existing data.  It can, however, append new entries replacing older
ones.  This behaviour has to be stated explicitly.  These are the
rules that applies

 - It is always possible to store a new session using an existing key
   if the timestamp does not already exist.

 - If the name and timestamp already exists, execution will stop and
   an error will be raised if the contents of the urdlist is
   *different* from what is already stored.

 - If name, timestamp, and contents are *the same*, nothing will be
   stored in the database and execution will just move on.  This is
   very useful for verification, for example to make sure that the
   current version of the source code corresponds to the jobs on disk.

 - A new entry can replace an old one by specifying ``update=True`` in
   the ``build()``-call, like this example

   .. code-block::

     def main(urd):
       urd.begin('testlist', '2023-06-20', update=True)
       ...

The Urd server serves incoming requests one at a time, so there are no
races possible when the Urd database is serving multiple users.



Urd Database Timestamps
-----------------------

The ``timestamp`` used to access items may be expressed in one of the
following types/formats: ``date``, ``datetime``, ``int`` , ``(date,
int)``, ``(datetime, int)``, ``"date"``, ``"datetime"``, or
``"datetime+int"``.  If specified using a string, the following format
applies

.. code-block:: text

  "%Y-%m-%d %H:%M:%S.%f"


This is in line with Pythons datetime module.  See the Python datetime
documentation for more information.

A specific timestamp in string format can be truncated to represent a
wider time range. The following examples cover all possible cases ::

  '2016-10'                    # month resolution
  '2016-10-25'                 # day resolution
  '2016-10-25 15'              # hour resolution
  '2016-10-25 15:25'           # minute resolution
  '2016-10-25 15:25:00'        # second resolution
  '2016-10-25 15:25:00.123456' # microsecond resolution

  '2016-10-25+3'               # Example of timestamp + int
  ('2016-10-25', 3)            # equivalent to above

Note that
  - ``ints`` without ``datetimes`` sort first,
  - ``datetimes`` without ``ints`` sorts before ``datetimes`` with ``ints``,
  - shorter ``datetime`` strings sorts before longer ``datetime`` strings, and
  - timestamps must be > 0.



Truncating Urd Lists
--------------------

Data can never be erased from the urd database, but a *restart marker*
can be inserted at any time giving the appearance that everything
after the marker timestamp is removed, like in this example:

.. code-block::
    :caption: Urd session with restart marker.

    def main(urd):
	urd.truncate('testlist', '2023')
        ...

The above ``truncate`` call makes all entries in ``testlist`` that
are from 2023 or later inaccessible.

.. tip :: Truncating to zero gives the appearance of a completely
   empty urdlist.  Very useful during development.


.. note :: Data is never erased in the Urd transaction database.
   Furthermore, all data is stored in an *easily readable format*, so
   if data is believed to be "lost", it is possible to find it by
   looking in the database files.
