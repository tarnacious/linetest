from multiprocessing import Process, Queue
from nose.loader import TestLoader
from nose.core import TextTestRunner
from StringIO import StringIO
import sys
import os
from mutation.collect_hook import CollectStatements
from mutation.modify_hook import ModifyModule
from pdb import set_trace


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
    hook = CollectStatements()
    sys.meta_path.append(hook)
    success = run_tests()
    return success, hook.modules

def get_modules(queue):
    queue.put(_get_modules())

def mutate_and_test(q, module, index):
    hook = ModifyModule(module, index)
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
    hook = ModifyModule("factorial", 0)
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


(success, modules) =  fork_get_modules()
#(success, modules) = _get_modules()

print modules
print modules.keys()

run_fixture(modules)
#test()
for result in results:
    print result

#run_fixture()
