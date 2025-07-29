Urd Database - The Admin
========================

*No setup or admin is required* to use the Urd database in single user
mode.  The ``ax init`` command will set up an empty database, and the
Urd database server starts automatically when the exax server is
started using ``ax server``.

This chapter explains is to set up the Urd database server so that
its contents can be shared between different users or agents.



Setup a shared server
---------------------

To setup a standalone Urd server, two things are needed

  - a directory where the database can be stored, and
  - a ``passwd`` file (stored in the same directory) containing
    user-password pairs.

Passwords are used to prevent accidental *writing* into the wrong
urdlists.  The default name of the database directory is ``urd.db/``.
Here's how it can be done

.. code-block::

  mkdir urd.db
  <editor> urd.db/passwd  # where <editor> is editor of choice, i.e. emacs

The ``passwd`` file contains one user-password pair, separated by a colon,
per line, like in this example

.. code-block::
   :caption: Example ``passwd`` file.

   ab:absecret
   cd:cdsecret
   sh:shsecret
   prod:productionsecret

.. note:: Anyone can *read* from the database, but only users present
   in the ``passwd`` file can *write* to the database.

To launch the Urd server, do

.. code-block::
  :caption: start a standalone Urd server

  ax urd-server --listen=localhost:8888 --path=./urd.db

  # or "ax urd-server --listen=<[host:]port> --path=<path>" in general.

The server will serve requests from multiple users in the order that
they arrive.


Connecting to a Shared Urd Server
---------------------------------

To switch to a shared server, the url to the server needs to be
put into the ``accelerator.conf`` file.

By default, the *local* Urd database server is serving on a socket in
the project directory, and the default configuration file looks
something like this

.. code-block::
   :caption: ``accelerator.conf``: Local Urd server is on this socket

   urd: local .socket.dir/urd


To listen to an external shared Urd database server, change this to
<hostname>:<port> like this

.. code-block::
    :caption: ``accelerator.conf``: Shared Urd server is on port 12345 on localhost.

    urd localhost 12345

As soon as the exax server is restarted, it will start using the external shared server.

.. note::
    Remember to populate the ``passwd`` file in the shared Urd
    database server's ``urd.db`` directory to get write access.


To connect to a shared Urd database using a password, set the
``$URD_AUTH`` environvent variable to "user:password" for example
like this

 .. code-block::

    URD_AUTH=myusername:mysecret ax run mybuildscript



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
intended to be (more or less) human readable.
