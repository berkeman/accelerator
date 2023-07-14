The project configuration file
==============================

when exax server starts, it looks for a file named  ``accelerator.conf`` in these places...@@@


This file specifies location of input data, results, and workdirs, as
well as number of parallel processes, server connections, and Python
interpreter version.  The default values from ``ax init`` (@) are a
really good start.

Typically, the file is created using ``ax init`` but it is
straightforward to maintain it by hand.

The configuration file is a collection of key-value pairs.
Values are specified as

.. code-block::

   key: value

   # or for several values

   key:
         value1
         value2

where any number of leading whitespaces are ok.  Anything after a hash
sign (#) until the end of the line is regarded as a comment.

It is possible to use shell environment valiables as values, by
writing ``${VAR}`` or ``${VAR=DEFAULT}``.  This is particularly useful
for definition of workdirs, like in this example

.. code-block::

   workdirs:
        ${USER} /workdirs/${USER}/

so that the same confiuration file can be used by multiple users,
while having unique workdirs for each user.

-----

slices
   Number of parallel procecess to use in ``analysis()`` and number of
   slices in datasets, for example

   .. code-block::

       slices: 32

workdirs
   One or more workdirs visible to exax in ``name path`` format, one
   workdir per line, for example

   .. code-block::

        workdirs:
            dev  /workdirs/ab/anim
            abcd /workdirs/abcd/anum

target workdir
   Which workdir that exax should write to.  Default is the first
   workdir in the ``workdirs`` list.  Example

   .. code-block::

       target workdir: dev

method packages
   Which directories (Python packages) that exax should know about.
   Each package is a name of a directory or a name of a Python
   package.  Example:

   .. code-block::

       method packages:
                   dev                           auto-discover
                   accelerator.examples          auto-discover
                   accelerator.standard_methods

   The optional ``auto-discover`` makes all methods in the package
   executable, see @.


listen
   Where the exax servers listens for incoming connections.  This can
   be ``port``, ``host:port``, or a unix socket path.  Example

   .. code-block::

      # listen on a unix socket
      listen: .socket.dir/server

   or

   .. code-block::

      # listen on localhost port 8888
      listen: localhost:8888


board listen
   Where the exax Board server should listen for incoming connections.
   The syntax is similar to the ``listen`` directive.

   .. tip::

      If connecting to a server using ssh, a unix socket on the
      serving machine can be connected to a port on the local machine
      like this

      .. code-block:: sh

         ssh -L 9999:/path/to/project/.socket.dir/board <host>

      And then point the browser on the local machine to ``localhost:9999``.

urd
   How to reach the urd database server.  It can be either running
   and connected *locally*, like this

   .. code-block::

      urd: local .socket.dir/urd

   or *remotely*, like this

   .. code-block::

      urd: remote <host>:<port>

   The specification is otherwise similar to ``listen``.

   See @ for more information on standalone Urd servers.


result directory
   This is a path specifying where results should go.  Example

   .. code-block::

      result directory: ./results/

   Read more about result directory here @.


input directory
   A path to where input data files are stored.

   .. code-block::

      input directory: /path/to/the/data/

   Read more about the input directory here @.

   .. tip:: This decouples the path of the input data from exax.  As
            long as ``input directory`` is kept up to date, data can
            be moved around in the system without the need to update
            any source code.


interpreters
   This is where different Python interpreters are listed.  They can
   then be enabled independently for each method using the
   ``methods.conf`` file, see @.  Example

   .. code-block::

      interpreters:
          2.7 /path/to/python2.7
          test /path/to/beta/python

   The example above specifies two interpreters, named ``2.7`` and ``test``.

   .. tip:: Use this for code that requires a specific Python version
            or relies on a particular virtual environment.  It can be
            enabled on a single method only.

   .. tip:: It is easy to run multiple versions of, say, tensorflow,
            in the same project using this approach.
