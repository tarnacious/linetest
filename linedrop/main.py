import sys
from linedrop.mutation.collect_hook import CollectStatements
from linedrop.mutation.modify_hook import ModifyModule
#from runners.nose_runner import run_tests
from linedrop.runners.pytest_runner import run_tests
from linedrop.isolation.run_process import run_process
from itertools import groupby
import os


def get_modules(path):
    hook = CollectStatements(path)
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



def process_results(results):
    files = {}
    for key, group in groupby(results, lambda x: x[0]):
        files[key] = group
    print " "
    print files

def main():
    path = os.getcwd() + "/sample"
    (success, modules) = run_process(lambda: get_modules(path))
    print "success?", success
    print modules
    print modules.keys()
    results = run_fixture(modules)
    for result in results:
        print result

    process_results(results)

if __name__ == "__main__":
    path = os.getcwd() + "/sample"
    (success, modules) = get_modules(path)
    print modules.keys()
