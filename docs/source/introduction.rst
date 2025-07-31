What is Exax?
=============

Exax is a data processing framework designed to make development and
operations *faster* and with *fewer mistakes*.  Although exax
implements several novel ideas, there is one feature that stands out
and as will be shown later provides a number of exciting advantages:

**Things are computed only once.**

*Exax remembers all program executions, and can instantly return a previously computed result given input data, parameters, and program source code.*

In addition, a naive but simple to use parallell processing
environment helps speeding up many practical use cases significantly.

Exax has a small footprint, few dependencies, and can run on any
hardware ranging from a Raspberry Pi or laptop to a multi-processor
rack server.

For dashboarding and visualisation of results and program/dataflows,
exax has an integrated web server.

Read about more features below.



Design Goals
------------

Exax is designed to be

 - **fast**, because

   - it will re-use earlier computations to save execution time

   - it is very easy to write simple but very powerful *parallel* programs

   - it comes with a very fast streaming data container for large
     parallel datasets

   - in a collaborative environment, results are re-used between users

 - **transparent** and **reproducible**, meaning that

   - it is straightforward to validate that a specific result is the result of a specific run

   - there is an observable connection between results, source code, and input data

   - it is easy to inspect any step in the execution/data flow

 - **helpful in avoiding common mistakes**, because

   - there is no need for arbitrary intermediate *filenames* that can be mixed up

   - results can be verified to be up to date with source code and input data

 - **minimalistic**, because

   - it has a very small footprint

   - it has a minimum of dependencies



Some Key Highlights
-------------------

Exax remembers old computations, and will not re-compute anything that
has been computed before.  Computation re-use is a core part of the
methodology and “just works”.  This saves time and energy.

The simple parallel processing capabilities makes use of modern
multi-core processors and speed up computations correspondingly.

The transparent workflow, from input data and source code to computed
results, is easy to inspect, and exax will always show results that
are up to date with the project's source code.

Several users can work on the same project on the same machine, and
share results and intermediate computations without interfering with
eachother.

Exax is originally designed for back end processing of large live
running recommender systems.  It is therefore easy to operate.

A built in database, called the Urd database, may be used to store and
retrieve references to computations and results using simple human
readable keys.

The streaming *dataset* datatype stores typed data in a row-column
format suitable for parallel processing.  It can handle billions of
rows with thousands of columns easily, on a laptop.  When accessed,
the data is *streamed* from disk to the CPU cores, thereby avoiding
time consuming disk seek operations.
