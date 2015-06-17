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

It might take some time.

# Example

    ..

# How it works

On a higher level linedrop works by first running the tests, ensuring a
successful run and obverving what statements are executed. It then repeats
this, each time removing a statement.

There are few key parts that need to work. 

* Running the tests and getting the test result
* Observing and modifing the loaded source code
* Isolating the source code modifications and the tests

The tests are run by requiring the runners (pytest and nose) as dependencies
and then and then running them in the process.  



[pytest][http://pytest.org/latest/]
[coverage][https://pypi.python.org/pypi/coverage]
[ast][https://docs.python.org/2/library/ast.html]
[pep302][https://www.python.org/dev/peps/pep-0302/]
