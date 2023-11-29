The JobList Class
=================

The JobList is primarily used to record sequences of jobs in the order
that they are built.  Complete JobLists can also be stored and
retrieved using the Urd database (see @@@).


.. autoclass:: accelerator.build.JobList
   :members:
   :exclude-members: exectime

It is also possible to access entries in a jobList using ``[]``-notation, see @@




Accessing an element in the JobList
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A specific job in a JobList can be retrieved using either the
``get()`` function or the ``[]``-notation, see the following examples

.. code-block::
    :caption: Access an element in a JobList

    def main(urd):
        urd.build('myfirstmethod')
        urd.build('mysecondmethod')

        jl = urd.joblist

        job = jl.get('myfirstmethod')

        job = jl.get(-1)  # last job in joblist or None

        job = jl.get('bogus')  # returns None, since this is the default

        job = jl['bogus']  # Fails, since there is no default

.. tip::
   It is a common operation to extract the last job in a
   JobList.  This is easily done using ``joblist.get(-1)``.

.. tip:: If there are several jobs based on the same method, they
   cannot be separated using ``get()``.  Consider giving the jobs
   unique names in the build call to solve this, see @@@.



Filter JobList based on method
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``find()`` function is used to get a new JobList containing jobs
of a specific method, see this example

.. code-block::
    :caption: Filter a jobList

    def main(urd):
        urd.build('a', x=0)
        urd.build('b', x=1)
        urd.build('a', x=2)

        # get a JobList containing the first and last job from above
        ajobs = urd.joblist.find('a')
