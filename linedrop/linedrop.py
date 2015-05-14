import sys
from mutation.collect_hook import CollectStatements
from mutation.modify_hook import ModifyModule
#from runners.nose_runner import run_tests
from runners.pytest_runner import run_tests
from isolation.run_process import run_process
from itertools import groupby


def get_modules():
    hook = CollectStatements()
    sys.meta_path.append(hook)
    success = run_tests()
    return success, hook.modules


def mutate_and_test(module, index):
    hook = ModifyModule(module, index)
    sys.meta_path.append(hook)
    return run_tests()


def run_fixture(modules):
    results = []
    for key in modules.keys():
        statements = modules[key]
        for i in range(len(statements)):
            (line, statement) = statements[i]
            success = run_process(lambda: mutate_and_test(key, i))
            results.append((key, line, success, statement))
            print success
    return results


(success, modules) = run_process(lambda: get_modules())
#(success, modules) = get_modules()

print "success?", success
print modules
print modules.keys()

results = run_fixture(modules)

def process_results(results):
    files = {}
    for key, group in groupby(results, lambda x: x[0]):
        files[key] = group
    print " "
    print files

for result in results:
    print result

process_results(results)
