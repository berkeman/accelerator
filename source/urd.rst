More on the Urd Database
========================

users, keys, and permissions
----------------------------
@@ nomenklatur: urd key / urd list ?!

A reference to an urlist is composed of a *username* and an arbitrary
*list name*, separated by a slash, like this

  ``alice/import``

The hierarchy is always two levels.

In a build script, the user part is not mandatory.  Exax will
automatically prefix the listname with the name of the user executing
the build script.  So the user alice could refer to the list above
simply as ``import``.

It is possible to limit write access to the urd database for each
user, and this is done by setting passwords in the Urd server's
``passwd`` file.  (@@ ref ) If, for example, the ``passwd`` file
contains the line

.. code-block::
  :caption: contents of ``urd.db/passwd``

  production:secret

the user ``production`` needs to be authorised to write to the
``production`` lists.  User and password are set using the
``URD_AUTH`` shell variable, for example when launching the build
script like this:

.. code-block::
  :caption: run a build script as the user ``production`` with a password
	    for urd database authentication.
	    
  URD_AUTH=production:secret   ax run productionscript



Setup a shared server
---------------------

A standalone Urd server is needed to share information between several
users or agents executing build scripts.  By default, the Exax
server will automatically start a *local* Urd server, but a shared
server needs to be setup separately.

To setup a standalone Urd server, two things are needed

  - a directory where it can put its database, and
  - a ``passwd`` file (stored in the mentioned directory) containing user-password pairs.

The default name of the database directory is ``urd.db/``, so here's
how it can be done

.. code-block::
  
  mkdir urd.db
  <editor> urd.db/passwd  # where <editor> is editor of choice.

The ``passwd`` file is one user-password pair, separated by a colon, per line.

To launch the server, do

.. code-block::
  :caption: start a standalone Urd server

  ax urd-server --listen=<[host:]port> --path=<path>

Please check the ``ax urd-server`` command documentation for complete
reference. (@@ref)

.. argparse::
   :module: accelerator.shell.urd
   :func: createparser
   :prog: ax urd


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
