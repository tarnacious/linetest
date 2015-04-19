from nose.loader import TestLoader
from nose.core import TextTestRunner
import os
import os, fnmatch

module = "sample"
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


files = list(find_files(src, pattern))
print files

counts = flatten(map(expand_lines, files))

working_dir = os.path.join(os.getcwd(), "sample")
suites = TestLoader(workingDir=working_dir).loadTestsFromDir("sample")
runner = TextTestRunner()
suites = list(suites)

result = runner.run(suites[1])
print result.wasSuccessful()
print counts
