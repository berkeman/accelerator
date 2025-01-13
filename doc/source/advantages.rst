What is Exax?
=============

Exax is a data processing framework designed to make development
*faster* and with *fewer mistakes*.  It achieves this using two main
approaches:
  - exax remembers all program executions, and recalls previous
    results instead of having to re-computing them
  - exax implements a naive, yet efficient, and easy to use parallel
    processing environment

Exax can run on any hardware ranging from a Raspberry Pie or laptop to a
multi-processor rack server.

Exax has a built in web-server for visualisation of results and
dashboarding.

Read about more features below.



Design Goals
------------

Exax is designed to be

 - **fast**.  Three main reasons is is fast are:

   - it will re-use earlier computations to save execution time

   - it is very easy to write simple but very powerful *parallel* programs

   - it comes with a very fast streaming datatype for large parallel datasets

 - **transparent** and **reproducible**, meaning that

   - it is straightforward to validate that a specific output is the result of a specific run

   - there is an observable connection between results, source, and input data

   - it is easy to find previous results and computations

 - **helpful in avoiding common mistakes**, because

   - there is no need for arbitrary intermediate filenames that can be mixed up

   - results can be proven to be up to date with source code and input data

 - **minimalistic**, with a very small footprint and a **minimum of dependencies**



Some Key Highlights
-------------------

Exax remembers old computations, and will not re-compute anything that
has been computed before.  Computation re-use is a core part of the
methodology and “just works”.  This saves time and energy.

The simple parallel processing capabilities makes use of modern
multi-core processors and speed up computations correspondingly.

The transparent workflow, from input data and source code to computed
results, is easy to inspect, and Exax will always show results that
are up to date with the project's source code.

Several users can work on the same project on the same machine, and
share results and intermediate computations without interfering with
eachother.

Exax is not limited to analysis or development work.  It is originally
designed for back end processing of live running recommender systems,
and is therefore easy to operate.

There is a built in database, called the Urd database, where
references to computations and results can be stored and looked up
using simple human readable keys.  The database is also used for
sharing data and results between users.

The streaming *dataset* datatype stores typed data in a row-column
format.  It can handle billions of rows with hundreds of columns
easily, on a laptop.  When accessed, the data is streamed to the CPU
cores, thereby avoiding time consuming disk operations entirely.
