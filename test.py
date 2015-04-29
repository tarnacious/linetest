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

    def __init__(self, remove_at=None):
        self.items = []
        self.remove_at = remove_at

    def action(self, node):
        if isinstance(node, ast.stmt):
            self.items.append((node.lineno, node))
            #print node.lineno, node
            return True
        return False

    def visit(self, node):
        #print len(self.items), self.remove_at
        if self.action(node) and len(self.items) == self.remove_at:
            print "REMOVING", node
            return ast.Pass()
        return super(ast.NodeTransformer, self).visit(node)


class ModifyImportHook(object):
    def __init__(self, module_name, index):
        self.module_name = module_name
        self.index = index
        self.current = 0

    def find_module(self, module_name, package_path):
        if module_name == self.module_name:
            return self
        return None

    def load_module(self, module_name):
        print "modify module:", module_name, self.index
        module = find_module(module_name)
        text = module[0].read()
        tree = ast.parse(text)
        transformer = Transformer(remove_at=self.index)
        node = transformer.visit(tree)

        ast.fix_missing_locations(tree)
        #print ast_visit(node)
        print "^^^"
        compiled = compile(tree, filename="<ast>", mode="exec")
        mymodule = imp.new_module(module_name)
        exec compiled in mymodule.__dict__
        return mymodule


class ImportHook(object):
    def __init__(self):
        self.modules = {}

    def find_module(self, module_name, package_path):
        if module_name.startswith("factorial"):
            return self
        return None

    def load_module(self, module_name):
        print "Load module:", module_name
        module = find_module(module_name)
        text = module[0].read()
        tree = ast.parse(text)
        transformer = Transformer()
        node = transformer.visit(tree)
        print ast_visit(tree)
        self.modules[module_name] = transformer.items
        compiled = compile(tree, filename="<ast>", mode="exec")
        mymodule = imp.new_module(module_name)
        exec compiled in mymodule.__dict__
        return mymodule


def run_tests():
    working_dir = os.path.join(os.getcwd())
    stream = StringIO()
    suites = TestLoader(workingDir=working_dir).loadTestsFromDir("./test")
    runner = TextTestRunner(stream=stream)
    runner = TextTestRunner()
    suites = list(suites)
    baseline = runner.run(suites[0])
    return baseline.wasSuccessful()


def get_modules(queue):
    hook = ImportHook()
    sys.meta_path.append(hook)
    success = run_tests()
    queue.put((success, hook.modules))

q = Queue()
p = Process(target=get_modules, args=(q,))
p.start()
p.join()
(success, modules) = q.get()
print success, modules

def mutate_and_test(q, module, index):
    hook = ModifyImportHook(module, index)
    sys.meta_path.append(hook)
    result = run_tests()
    q.put(result)

results = []

def run_fixture():
    for key in modules.keys():
        statements = modules[key]
        for i in range(len(statements)):
            (line, statement) = statements[i]
            print "Removing", statement, "on line", line, "in module", key
            q = Queue()
            p = Process(target=mutate_and_test, args=(q, key, i))
            p.start()
            p.join()
            if not q.empty():
                success = q.get()
            else:
                success = False
            results.append((key, line, success, statement))
            print success




def test():
    hook = ModifyImportHook("factorial", 9)
    sys.meta_path.append(hook)
    try:
        print "TRY"
        result = run_tests()
        print "CATCH", result
    except:
        print "ERROR"



run_fixture()
#test()
for result in results:
    print result

#run_fixture()
