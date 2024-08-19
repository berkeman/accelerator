Introduction to The Urd Database
================================

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


How is Data Stored?
-------------------

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


The Automatic Urd Session
-------------------------

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



Manual Urd Sessions
-------------------

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

In the example above, the urdlist only reflects the list's descriptive
name.  If the user part is implicit, like in this case, the value of
the shell variable ``$USER`` will be used under the hood.  The example
also specifies the name of the urdlist twice, in both the ``begin()``
and ``finish()`` functions.  This is a requirement and safety measure
to prevent unnecessary writes to the wrong urdlist.  If the names
differ, execution will stop and raise an error.


.. note:: An urdlist is always composed of two parts: user and a name,
   such as ``alice/import``.  If only one name is given, like
   ``import``, the user is implicit and the shell variable ``$USER``
   is used instead.

.. note:: The name specified in the ``begin()`` and ``finish()``
          functions *must be the same*.

.. note:: Urd sessions cannot be nested.  A second ``begin()`` without
          a ``finish()`` call inbetween will cause a failure.

.. tip:: The user part is very convenient to use when several
          programmers work in the same project.  It also enables the
          use of "virtual" users for the sake of separation.


Ending a Manual Urd Session
---------------------------

There are three ways to end an urd session:

- execute the ``urd.finish()`` call and have the session
  recorded/rejected/ignored.

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

A new urd session can be initiated once the previous is finished or aborted.
Only one urd session can be active at a time.



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

The server serves requests one at a time, so there are no races
possible when the Urd database is serving multiple users.


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

.. tip ::  Truncating to zero gives the appearance of a completely empty urdlist.


.. note :: Data is never erased in the Urd transaction database.
   Furthermore, all data is stored in an *easily readable format*, so
   if data is believed to be "lost", it is possible to find it by
   looking in the database files.





