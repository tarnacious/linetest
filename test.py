from multiprocessing import Process, Queue
from nose.loader import TestLoader
from nose.core import TextTestRunner
from StringIO import StringIO
import os
import os, fnmatch

src = "sample/src"
pattern = "*.py"

def find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename

def lines(path):
    return sum(1 for line in open(path))

def expand_lines(path):
    return [(path, line) for line in range(lines(path))]

def flatten(l):
    return sum(l, [])

def skip(l, i):
    return l[0:i] + l[i+1:]


files = list(find_files(src, pattern))
counts = map(expand_lines, files)


def run_tests(queue):
    working_dir = os.path.join(os.getcwd(), "sample")
    stream = StringIO()
    suites = TestLoader(workingDir=working_dir).loadTestsFromDir("sample")
    runner = TextTestRunner(stream=stream)
    suites = list(suites)
    baseline = runner.run(suites[1])
    queue.put(baseline.wasSuccessful())



results = []

for filename in files:
    with open(filename) as f:
        lines = f.readlines()
    for line in range(len(lines)):
        with open(filename, "w") as f:
            f.writelines(skip(lines, line))

        pycfiles = list(find_files(src, "*.pyc"))
        for pycfile in pycfiles:
            os.remove(pycfile)

        queue = Queue()
        p = Process(target=run_tests, args=(queue,))
        p.start()
        p.join()

        result = queue.get()
        results.append((filename, line + 1, result))

    # restore file
    with open(filename, "w") as f:
        f.writelines(lines)

for result in results:
    print result
