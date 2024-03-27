Introduction and Advantages
---------------------------

Exax is a data processing framework.  It has many applications in for
example data science, data engineering, and not least operations.

Exax is designed to be

 - **fast**.  The two main reasons is is fast are:

   - it will re-use earlier computations to save execution time

   - it is very easy to write simple but very powerful *parallel* programs

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

