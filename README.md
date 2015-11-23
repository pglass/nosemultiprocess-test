Overview
--------

This is a little repository demonstrating a few little problems with how `nose`
runs tests in multiple processes. Then it goes over how to make nose run way
better.

The `tests/` module contains two modules:

- `test_small.py` has a class with 2 test cases
- `test_large.py` has a class with 9 test cases (many more)

Every test function is identical:

- Every test case will take about 2 seconds
- Every test case will log the current and parent process ids
- Every test case will fail

Setup
-----

Just `pip install nose` and you're good to go.


Examples of nose's default behavior
-----------------------------------

### No multiprocess plugin

There's nothing out of the ordinary here.

**Command**: `nosetests -v tests/`

**Result**:

- 11 tests take about 22 seconds
- The result of each test case is output immediately
- Every test is run in the same process

### Multiprocess plugin, 1 process

There's no ouput at all until all the tests have finished.

**Command**: `nosetests -v --processes=1 tests/`

**Result**:

- 7 of 11 tests ERROR with a `TimedOutException` from `nose/plugins/multiprocess.py`
- The tests take 10-11 seconds
- We don't see any output until after all the tests have finished!
- All tests are run in the same process


### Multiprocess plugin, 1 process (process timeout=60)

We need to raise the process timeout to allow a sufficient amount of time for
the child process to run all of its tests. This requires we anticipate how long
our tests will take to run. (The default process timeout is 10 seconds.)

**Command**: `nosetests -v --processes=1 --process-timeout=60 tests/`

**Result**:

- The tests take about 22 seconds
- We see no output until all test cases in a module have completed.
- We see additional output each time nose finishes running a module. (It first
spits the results of tests cases in `test_large.py` and then the results for
test cases in `test_small.py`.)
- All tests are run in the same process


### Multiprocess plugin, 2 processes

Each module's tests are run entirely in one process. We are still plagued by
nose's default process timeout (10 seconds).

**Command**: `nosetests -v --processes=2 tests/`

**Result**:

- 5 of 11 tests ERROR with a `TimedOutException` from `nose/plugins/multiprocess.py`
- The tests take about 10-11 seconds to complete
- We see no output until all test cases in a module have completed (in this
case, `test_small.py` has fewer test cases so wee see the results of that
module print first)
- All test cases in `test_small.py` are run in one process. All test cases in
`test_large.py` are run in the second process.


### Multiprocess plugin, 2 processes (process timeout=60)

The process timeout gets rid of TimedOutExceptions. Nose only maps modules
across processes, rather than mapping test cases across processes.

**Command**: `nosetests -v --processes=2 --process-timeout=60 tests/`

**Result**:

- The tests take about 18 seconds to execute.
- We see no output until all test cases in a module have completed (in this
case, `test_small.py` has fewer test cases so wee see the results of that
module print first)
- All test cases in `test_small.py` are run in one process. All test cases in
`test_large.py` are run in the second process.


### Multiprocess plugin, 3 processes (process timeout=60)

**Command**: `nosetests -v --processes=3 --process-timeout=60 tests/`

**Result**: The result is identical to using two processes with a process timeout
of 60. The third process was entirely unused!


How to fix this
---------------

Nose actually provides a way to specify that a test class/module can be split
up across multiple processes. You need add `_multiprocess_can_split_ = True` to
your test class/module. Unfortunately, you have to modify your code to add this
attribute. Nose does not have a flag that tells it to default to splitting up
classes/modules across processes. (I wrote [this nose plugin](
https://pypi.python.org/pypi/nose-mp-split) to resolve that).

Take aways
----------

- By default, nose maps classes across processes. It _can_ distribute
individual test cases acrosses worker processes, but instead assumes the tests
it's running are not safe to parallelize. This meant adding more processes
than we had classes was pointless. Nose refused to run tests in more that two
of the processes.
- Nose's default process timeout was pretty silly for our use case. In this
case, we had 11 test cases that took two seconds each, and we immediately hit
the process timeout. It's pretty easy to have 5+ second test cases when writing
functional tests against asyncronous APIs (you're over the default process
timeout with just two 5+ second test cases in the same class).
- When running with multiple processes, the worker process must finish running
all of its assigned test cases before any output is printed. When we combine
this behavior with an uneven distribution of test cases across processes, we're
left waiting quite a while wondering why our tests are hanging.
