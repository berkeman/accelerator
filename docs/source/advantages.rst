Introduction and Advantages
---------------------------

Säga något om att dela jobb *på samma filsystem*.

configure board

- result_directory

.. code-block::
    :caption: Create a link to a file created by job1 to ``result_directory``.

    def main(urd):
        job = urd.build('awesome_method', x=3)
	job.link_result('outfile.txt')

In the last example, the resulting file created by the
``awesome_method`` job is considered to be of value for a human
observer and will therefore appear (as a soft link) in the ``result
directory`` and on the start page of *Board*. (@@@)

  Note the
  "``['inputs']``" above that specifies a list of input datasets with
  the name "``input``".  


.. tip :: The "``result directory``" should be the place to find files
  that are considered to be relevant "output" from a project run.  Soft
  links in the result directory link to files in jobs using the
  ``job.link_result()`` function (@).

- working with data files

 input directory
 input_filename

-visualising results

 result directory

-descriptions in build scripts


Exax is a data processing framework.  It has many applications in for
example data science, data engineering, and not least operations.

Exax is designed to be

 - **fast**.  The two main reasons is is fast are:

   - it will re-use earlier computations to save execution time

   - it is very easy to write simple but very powerful *parallel* programs

   - it comes with a very fast streaming datatype for large parallel datasets

 - **transparent** and **reproducible**, meaning that

   - it is straightforward to validate that a specific output is the result of a specific run

   - there is an observable connection between results, source, and input data

 - and in addition it is easier to **avoid common mistakes**, because

   - there is no need for arbitrary intermediate filenames that can be mixed up

   - an unchanged program will re-run in a fraction of a second in order to validate a result

Exax remembers old computations, and will not re-compute anything that
has been computed before.  This saves time and energy.  The simple
parallel processing capabilities makes use of modern multi-core
processors and speed up computations correspondingly.  (A standard
eight core CPU can do one CPU-core-hour of work in just 7.5 minutes.)
The transparent workflow, from input data and source code to computed
results, is easy to inspect, and Exax will always show results that
are up to date with the project's source code.

The Urd database is used to store references to previous computations
so that any computed result can be fetched and used at a later time
without any recomputations.  The database is also used for sharing
data and results between users.

All computations done by exax are stored on disk and registered so
that they can be re-used later.  Computation re-use is a core part of
the methodology and "just works".

The streaming *dataset* datatype stores typed data in a row-column
format.  It can handle billions of rows with hundreds of columns
easily, on a laptop.  When accessed, the data is streamed to the CPU
cores, thereby avoiding time consuming disk ``seek()`` operations
completely.
