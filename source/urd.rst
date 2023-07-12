More on the Urd Database
========================

The Urd database is used to store references to built jobs
persistently, and to make it simple to share data and results between
users and scripts.  Basic usage is covered in section @.


Users, Keys, and Permissions
----------------------------

A reference to an urd list is composed of a *username* and a *list
name*, separated by a slash, like this

  ``alice/import``

The hierarchy is always two levels, but in a build script, the user
part is not mandatory.  Exax will automatically prefix the list name
with the name of the user executing the build script.  So the user
``alice`` could refer to the list above simply as ``import``, like this

.. code-block::

   def main(urd):
       item = urd.peek('import', '2020-02-20')
       # for user "alice" this is the same as
       item = urd.peek('alice/import', '2020-02-20')


The Urd database is transparently readable for everyone, but it is
possible to limit *write* access to the urd database for each user.
This is done by setting passwords in the Urd server's ``passwd`` file.
(@@ ref ) If, for example, the ``passwd`` file contains the line

.. code-block::
  :caption: contents of ``urd.db/passwd``

  production:secret

the user ``production`` needs to be authorised to write to the
``production`` lists (and the password is ``secret``).  User and
password are set using the ``$URD_AUTH`` shell variable, for example
when launching the build script like this:

.. code-block:: sh
  :caption: Run a build script as the user ``production`` with a
            password for urd database authentication.

  URD_AUTH=production:secret ax run productionscript

.. tip :: Use $URD_AUTH to protect against accidental writes when
   multiple users share the same Urd server.



Setup a shared server
---------------------

A standalone Urd server is needed to share information between several
users or agents executing build scripts.  By default, the exax server
will automatically start a *local* Urd server, but a shared server
needs to be setup separately.

To setup a standalone Urd server, two things are needed

  - a directory where the database can be stored, and
  - a ``passwd`` file (stored in the same directory) containing
    user-password pairs.

The default name of the database directory is ``urd.db/``, so here's
how it can be done

.. code-block::
  
  mkdir urd.db
  <editor> urd.db/passwd  # where <editor> is editor of choice.

The ``passwd`` file is one user-password pair, separated by a colon,
one entry per line, like in this example

.. code-block::
   :caption: Example ``passwd`` file.

   ab:absecret
   cd:cdsecret
   sh:shsecret
   prod:productionsecret


To launch the server, do

.. code-block::
  :caption: start a standalone Urd server

  ax urd-server --listen=<[host:]port> --path=<path>

Please check the ``ax urd-server`` command documentation for complete
reference. (@@ref)

The server will serve requests from multiple users in the order that
they arrive.



Directory Structure of the Urd Database
---------------------------------------

The Urd database has the following structure

.. code-block::

  database_root/
                passwd
                user1/
                      list1
                      list2
                user2/
                      list3

Each list-file is a transaction log, where each new transaction is
appended to the end of the file.  It is written in plain text and
intended to be more or less human readable.
