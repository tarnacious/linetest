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

class Transformer(ast.NodeTransformer):

    def __init__(self, remove_at=None):
        self.items = []
        self.remove_at = remove_at

    def get_statement(self, node):
        if isinstance(node, ast.stmt):
            return (node.lineno, node)

    def visit(self, node):
        statement = self.get_statement(node)
        if statement:
            if len(self.items) == self.remove_at:
                self.items.append(statement)
                return ast.Pass()
            self.items.append(statement)
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
        if module_name.startswith("sample"):
            return self

    def _get_module(self, module_name):
        parts = module_name.split(".")
        if len(parts) > 1:
            parent = ".".join(parts[:-1])
            return sys.modules[parent]

    def _is_package(self, _file):
        return _file is None

    def _get_name(self, module_name):
        return module_name.split(".")[::-1][0]

    def _get_filename(self, _file, path):
        if _file:
            return _file.name
        return "%s/__init__.py" % path

    def _get_code_string(self, _file, path):
        if _file:
            return _file.read()
        filename = self._get_filename(_file, path)
        with open(filename, "r") as f:
            return f.read()

    def load_module(self, module_name):
        name = self._get_name(module_name)
        module = self._get_module(module_name)
        if module:
            found = find_module(name, module.__path__)
        else:
            found = find_module(module_name)

        (_file, pathname, description) = found
        text = self._get_code_string(_file, pathname)
        if False: # _file:
            tree = ast.parse(text)
            transformer = Transformer()
            node = transformer.visit(tree)
            self.modules[module_name] = transformer.items
            compiled = compile(tree, filename="<ast>", mode="exec")
            mymodule = imp.new_module(module_name)
            exec compiled in mymodule.__dict__
            return mymodule
        else:
            tree = ast.parse(text)
            transformer = Transformer()
            node = transformer.visit(tree)
            self.modules[module_name] = transformer.items
            compiled = compile(tree, filename="<ast>", mode="exec")

            mymodule = imp.new_module(module_name)
            mymodule = sys.modules.setdefault(module_name, mymodule)


            if self._is_package(_file):
                mymodule.__path__ = [pathname]

            mymodule.__file__ = self._get_filename(_file, pathname)
            mymodule.__loader__ = self
            #mymodule.__package__ = module_name

            exec(compiled, mymodule.__dict__)
            print "imported", module_name
            return mymodule


def run_tests():
    working_dir = os.path.join(os.getcwd())
    stream = StringIO()
    suites = TestLoader(workingDir=working_dir).loadTestsFromDir("./test")
    runner = TextTestRunner(stream=stream)
    runner = TextTestRunner()
    suites = list(suites)
    results = []
    for suite in suites:
        results.append(runner.run(suite))

    bools = [x.wasSuccessful() for x in results]
    return all(bools)

def _get_modules():
    hook = ImportHook()
    sys.meta_path.append(hook)
    success = run_tests()
    return success, hook.modules

def get_modules(queue):
    queue.put(_get_modules())

def mutate_and_test(q, module, index):
    hook = ModifyImportHook(module, index)
    sys.meta_path.append(hook)
    result = run_tests()
    q.put(result)

results = []

def run_fixture(modules):
    for key in modules.keys():
        statements = modules[key]
        for i in range(len(statements)):
            (line, statement) = statements[i]
            print "Removing(%s)" % i, statement, "on line", line, "in module", key
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
    hook = ModifyImportHook("factorial", 0)
    sys.meta_path.append(hook)
    try:
        print "TRY"
        result = run_tests()
        print "CATCH", result
    except:
        print "ERROR"


def fork_get_modules():
    q = Queue()
    p = Process(target=get_modules, args=(q,))
    p.start()
    p.join()
    return q.get()


#(success, modules) =  fork_get_modules()
(success, modules) = _get_modules()

print modules
print modules.keys()

#run_fixture(modules)
#test()
for result in results:
    print result

#run_fixture()
