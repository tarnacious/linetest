from multiprocessing import Process, Queue
from nose.loader import TestLoader
from nose.core import TextTestRunner
from StringIO import StringIO
import os, fnmatch
from imp import find_module, load_source, new_module
import ast
import imp
import sys

from pdb import set_trace

def str_node(node):
    if isinstance(node, ast.AST):
        fields = [(name, str_node(val)) for name, val in ast.iter_fields(node) if name not in ('left', 'right')]
        rv = '%s(%s' % (node.__class__.__name__, ', '.join('%s=%s' % field for field in fields))
        return rv + ')'
    else:
        return repr(node)

def ast_visit(node, level=0):
    print('  ' * level + str_node(node))
    for field, value in ast.iter_fields(node):
        if isinstance(value, list):
            for item in value:
                if isinstance(item, ast.AST):
                    ast_visit(item, level=level+1)
        elif isinstance(value, ast.AST):
            ast_visit(value, level=level+1)


class Transformer(ast.NodeTransformer):
    def visit_Print(self, node):
        print node.lineno, "print"
        ast_visit(node)
        for node2 in node.values:
            node2.s = node2.s + "!!!"
        return node



class ImportHook(object):
    def __init__(self):
        self.name = "initial"

    def find_module(self, module_name, package_path):
        #print self.name,  module_name, package_path
        if module_name.startswith("factorial"):
            return self
        if module_name.startswith("sample") and package_path:
            #print "---", module_name, package_path
            #source = load_source(module_name, package_path[0])
            #print source
            pass
        return None

    def load_module(self, module_name):
        print "Load module:", module_name
        module = find_module(module_name)
        text = module[0].read()
        tree = ast.parse(text)
        #print ast_visit(tree)

        node = Transformer().visit(tree)


        for stmt in ast.walk(tree):
            if isinstance(stmt, ast.ClassDef):
                continue
            #print stmt
            # Ignore non-class
            if not isinstance(stmt, ast.ClassDef):
                #print stmt
                #items = stmt.body
                #print items[0].lineno #, items[0].names
                continue

        compiled = compile(tree, filename="<ast>", mode="exec")
        mymodule = imp.new_module(module_name)
        exec compiled in mymodule.__dict__
        return mymodule


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
    runner = TextTestRunner(stream=stream)
    runner = TextTestRunner()
    suites = list(suites)
    baseline = runner.run(suites[0])
    queue.put(baseline.wasSuccessful())



print "starting"

print "appending"
hook = ImportHook()
sys.meta_path.append(hook)

print "test run1"
q = Queue()
run_tests(q)
print q.get()
#hook.name = "test run one"
#p = Process(target=run_tests, args=(q,))
#p.start()
#p.join()
#print q.get()
#hook.name = "test run two"
#p = Process(target=run_tests, args=(q,))
#p.start()
#print q.get()
#p.join()
