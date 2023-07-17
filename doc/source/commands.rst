ax commands
===========

Mention C-t somewhere!



history operators
-----------------

Use '~' to go to the earlier current job
Use '^' to go to the previous job (or dataset, using {jobs/datasets}.parent
usr '+' to go to next future job
several '~' or '+' may be used after eachother, like 'job~~~++ == job~+~+~ == job~'
use '.previous', '.jobs.source', etc to jump to other job
use number together with '~' and '+', like this '~10'
<, > prev/next job i same workdir
! ensure current job

jobid
ax job :urdlist/timestamp: sista jobbet i den listan
ax job :urdlist/timestamp^: sista jobbet i föregående lista
ax job :urdlist/timestamp:-3 tredje sista
ax job :urdlist/timestamp:0 första
~ ger nästa

urd history operators
---------------------
ax urd list ger sista i list
ax urd :list: samma
ax urd :list^: ger item före sista i list osv.





Remains:

-         abort  abort running job(s)
-         alias  show defined aliases
-  board-server  runs a webserver for displaying results
-            gc  delete stale and unused jobs
-          grep  search for a pattern in one or more datasets
-         intro  show introduction text
-        method  information about methods
-           run  run a build script
-        script  information about build scripts
-        server  run the main server
-        status  server status (like ^T when building)
-    urd-server  run the urd server
-       version  show installed accelerator version
-       workdir  information about workdirs

Fixed:

-            ds  display information about datasets
-           urd  inspect urd contents
-           job  information about a job
-          init  create a project directory


ax init
-------

.. argparse::
   :ref: accelerator.shell.init.createparser
   :prog: ax init
   :nodescription:

   Set up a new project directory hierarchy.  Default location is
   current directory.

   The command creates

   - a project configuration file "``accelerator.conf``",
   - a method directory ("``./dev``" by default),
   - a workdir ("``workdirs/dev``" by default"), and
   - a result directory ("``./result_directiory``")

   It also performs a ``git init`` by default.

   .. note:: After running this command, you probably what to have a look
             at, and perhaps modify, ``accelerator.conf``.


   DIR : @replace
      Name of project directory to create.  If omitted, the current directory
      will be used.

   --slices : @replace
      By default, the number of slices will be set to the number of
      available CPU cores.  Use this to override.

   --name : @replace
      Name of method dir *and* workdir, default is “``dev``”.

   --input : @replace
      Input directory, i.e., path to directory where input files are stored.

      .. NOTE:: This is not set by default!

   --force : @replace
      Go ahead even though directory is not empty, or workdir exists with incompatible slice count.
      The default behaviour is to *not* proceed.

   --tcp : @replace
      Listen on TCP instead of unix sockets.
      Specify HOST (can be IP) to listen on that host specify PORT to use range(PORT, PORT + 3) specify both as HOST:PORT
      **@@@ vad 17 står det här???**
      Default: False

   --no-git : @replace
      Don't create git repository (run ``git init``) in project directory.  The default is to create it.

   --examples : @replace
      Copy example files to project directory.  Useful for inspection and execution of built-in example code.
      The default is to *not* copy these files.



ax urd
------

.. argparse::
   :ref: accelerator.shell.urd.createparser
   :prog: ax urd

   path : @before
       A path


ax job
------

.. argparse::
   :ref: accelerator.shell.job.createparser
   :prog: ax job
   :nodescription:

   Used to inspect jobs.



ax ds
-----

.. argparse::
   :ref: accelerator.shell.ds.createparser
   :prog: ax ds
