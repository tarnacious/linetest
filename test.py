from multiprocessing import Process, Queue
from nose.loader import TestLoader
from nose.core import TextTestRunner
from StringIO import StringIO
import os, fnmatch
from imp import find_module, load_source, new_module
import ast




import sys
class Restriction(object):
    @classmethod
    def add(cls, module_name):
        print "add", module_name

    def find_module(self, module_name, package_path):
        ##print module_name, package_path
        if module_name.startswith("factorial"):
            print "catch factorial", module_name, package_path
            return self
        if module_name.startswith("sample") and package_path:
        #if module_name.startswith("factorial"):
            print "---", module_name, package_path
            print "<<"
            #print module_name.split(".")[0]
            #module = find_module(module_name.split(".")[0], package_path[0])
            #print module
            source = load_source(module_name, package_path[0])
            print source
            #from pdb import set_trace
            #set_trace()
        return None
        return self

    def load_module(self, module_name):
        print "###", module_name

        module = find_module(module_name)
        print module[0].read()
        tree = ast.parse(module[0].read())
        print tree
        #compiled = compile(tree, filename="<ast>", mode="exec")
        #print compiled

        mynamespace = {}
        print ">>>>"
        #exec(compiled, mynamespace)
        print "<<<<"
        #import pdb
        #pdb.set_trace()
        #print mynamespace["factorial"]

        class ns:
            def factorial(self, n):
                return 1

        return ns()
        #raise ImportError("Restricted")

print "appending"
sys.meta_path.append(Restriction())

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
    working_dir = os.path.join(os.getcwd())
    stream = StringIO()
    suites = TestLoader(workingDir=working_dir).loadTestsFromDir("./test")
#    runner = TextTestRunner(stream=stream)
    runner = TextTestRunner()
    suites = list(suites)
    baseline = runner.run(suites[0])
    print baseline
    queue.put(baseline.wasSuccessful())



def testme():
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

print "starting"
q = Queue()
run_tests(q)
