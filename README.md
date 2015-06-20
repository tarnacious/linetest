# Line Drop

A mutation testing tool that removes every statements from the source one by
one and runs test suite for each mutation. It then reports if the entire test
suite passed for each mutation.

This is a pretty bad idea from many reasons, but it can show that although
statements are reported as covered by [coverage][coverage] it does not mean
they are required for the tests to pass.

# Using Line Drop

As this is still a bit of hack and a pretty bad idea it isn't on PyPI, however
it can be installed from a git repository into a Python (2.7) environment with
`pip`.

    pip install git+https://github.com/tarnacious/linetest.git
    
It can then be invoke like [pytest][pytest] except the program is called
`linetest` and the first parameter is regular expression that should match all
the modules to be mutated.

    linedrop ^my_module.*$ path/to/my/tests/


# Example

There is a small example target project in this repository.

    $ git clone https://github.com/tarnacious/linetest.git .
    $ virtualenv -p /usr/bin/python2.7 .
    $ ./bin/python setup.py develop

Not we can run pytest with coverage on the sample project:

    $ ./bin/py.test --cov sample test_sample/
    ===================================================== test session starts =====================================================
    platform darwin -- Python 2.7.9 -- py-1.4.28 -- pytest-2.7.1
    rootdir: /Users/tarn/projects/linedrop, inifile:
    plugins: cov
    collected 5 items

    test_sample/test_add.py .
    test_sample/test_factorial.py ....
    --------------------------------------- coverage: platform darwin, python 2.7.9-final-0 ---------------------------------------
    Name                        Stmts   Miss  Cover
    -----------------------------------------------
    sample/__init__                 0      0   100%
    sample/factorial                9      0   100%
    sample/subsample/__init__       0      0   100%
    sample/subsample/add            2      0   100%
    -----------------------------------------------
    TOTAL                          11      0   100%

    ================================================== 5 passed in 0.05 seconds ===================================================

We see that all the test pass and coverage is 100% over 11 statements. We can now run the same tests with linedrop.

    $ ./bin/linedrop ^sample.* test_sample/
    Using module pattern: ^sample.*
    Starting statement discovery.
    Discovery complete, tests pass.
    Completed 1 of 11 False
    Completed 2 of 11 False
    Completed 3 of 11 False
    Completed 4 of 11 False
    Completed 5 of 11 False
    Completed 6 of 11 True
    Completed 7 of 11 True
    Completed 8 of 11 False
    Completed 9 of 11 False
    Completed 10 of 11 False
    Completed 11 of 11 False
    sample.factorial                                1       False   FunctionDef
    sample.subsample.add                            1       False   FunctionDef
    sample.subsample.add                            2       False   Return
    sample.factorial                                3       False   If
    sample.factorial                                4       False   Raise
    sample.factorial                                6       True    If
    sample.factorial                                7       True    Return
    sample.factorial                                9       False   Assign
    sample.factorial                                13      False   Return
    sample.factorial                                11      False   Assign
    sample.factorial                                10      False   For

    Writing formated results to linedrop_results.txt
    Writing results to linedrop_results.json

    Done.

This shows us the although lines 6 and 7 are covered, they are not required for the tests to pass. Here is the module: 

    1   def factorial(n):
    2
    3       if n < 0:
    4           raise ValueError
    5
    6       if n == 0:
    7           return 1
    8
    9       factorial = 1
    10      for i in range(1, n + 1):
    11          factorial = factorial * i
    12
    13      return factorial

As you can see, although lines 6 and 7 are not incorrect, they are not required
as the value 1 will be returned anyway.

# How it works

On a higher level linedrop works by first running the tests, ensuring a
successful run and obverving what statements are executed. It then repeats
this, each time removing a statement.

There are few key parts that need to work. 

* Running the tests and getting the test result
* Observing and modifying the loaded source code
* Isolating the source code modifications and the tests

The tests are run by requiring the runners (pytest and nose) as dependencies
and then and then running them in-process. For pytest, calling the main entry
point works pretty well as it takes all it's configuration from `sys.argv`
which is pretty much exactly what we want. For nose, a bit more work is
required and currently only a proof of concept nose runner is included. 

Observing and modifying the source are implemented using a combination of the
`sys.metapath` import hook that was introduced in [PEP 302][pep302], the
[`ast`][ast] module to inspect, modify and load abstract syntax trees from
python source and the [`imp`][imp] module that exposes some of the import
mechanics.

Due to the way the code is modified (via an import hook) and the way imports
work in Python (they are only imported once) and we want modify an import more
than once some form of isolation or module unloading is required. This is
achieved by forking the process before the tests are run and modifying the
imports in each for each mutation in a separate process. This also makes it
possible to run mutation and test suite runs in parallel.

# Does it work

The was initially built to test some in-house software at [Retresco][retresco]
and for this software it worked.

I am currently testing it out of two opensource projects I selected due to very
high test coverage. These are [premailer][premailer] which is quite small and
[pyramid][pyramid] which is a quite a lot bigger in terms of number of lines
and tests. Currently the premailer tests seem to work and return pretty good results

# Things to do

Some things that I would like to get done in no particular order:

* Python 3 support! (I started with 2.7 as I needed to test a 2.7 project)
* Log everything to a log file
* Get the nose test runner working
* Customizable concurrency 
* Test on more projects
* Unittests for linedrop itself
* Running linedrop on itself
* Better output
* Coverage compatable reports
* Docstring tests
* Code clean-up (it's still a bit of mess)
* Remove six dependency and manual test, unittest multiple metapath functions.


[pytest]: http://pytest.org/latest/
[coverage]: https://pypi.python.org/pypi/coverage
[ast]: https://docs.python.org/2/library/ast.html
[pep302]: https://www.python.org/dev/peps/pep-0302/
[imp]: https://docs.python.org/2/library/imp.html
[pyramid]: https://github.com/Pylons/pyramid
[premailer]: https://github.com/premailer/premailer
[retresco]: http://www.retresco.de/
