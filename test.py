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
        print ">", module_name
        if module_name.startswith("factorial"):
            return self
        #if module_name == "sample":
        #    return self
        if module_name.startswith("sample"):
            return self
        return None

    def load_module(self, module_name):
        print "Load module:", module_name
        #set_trace()
        parts = module_name.split(".")
        if len(parts) > 1:
            parent = ".".join(parts[:-1])
            print "submodule"
            module = sys.modules[parent]
            set_trace()
            print type(module)
            print module
            print module.__path__
            (_file, pathname, description) = find_module(parts[1], module.__path__)
        else:
            (_file, pathname, description) = find_module(module_name)
        if _file:
            text = _file.read()
            tree = ast.parse(text)
            transformer = Transformer()
            node = transformer.visit(tree)
            self.modules[module_name] = transformer.items
            compiled = compile(tree, filename="<ast>", mode="exec")
            mymodule = imp.new_module(module_name)
            print "starting compile factoiral"
            exec compiled in mymodule.__dict__
            print "done compile factoiral"

            return mymodule
        else:
            print "Is a package!"
            filename = "%s/__init__.py" % pathname
            with open(filename, "r") as f:
                text = f.read()
                tree = ast.parse(text)
                transformer = Transformer()
                node = transformer.visit(tree)
                self.modules[module_name] = transformer.items
                compiled = compile(tree, filename="<ast>", mode="exec")

                mymodule = imp.new_module(module_name)
                mymodule = sys.modules.setdefault(module_name, mymodule)
                mymodule.__path__ = [pathname]
                mymodule.__file__ = filename
                mymodule.__loader__ = self
                #mymodule.__package__ = module_name

                exec compiled in mymodule.__dict__
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
    (success, hook.modules)
    queue.put()

#q = Queue()
#p = Process(target=get_modules, args=(q,))
#p.start()
#p.join()
#(success, modules) = q.get()
#print success, modules

(success, modules) = _get_modules()
print modules
print modules.keys()

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



#run_fixture()
#test()
for result in results:
    print result

#run_fixture()
