import sys
from linedrop.mutation.collect_hook import CollectStatements
from linedrop.mutation.modify_hook import ModifyModule
#from runners.nose_runner import run_tests
from linedrop.runners.pytest_runner import run_tests
from linedrop.isolation.run_process import run_process, run_processes
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

    funs = []
    for key in modules.keys():
        statements = modules[key]
        for i in range(len(statements))[:1]:
            (line, statement) = statements[i]
            funs.append((key, i))

    def update(result):
        statement = "no statement"
        (key, line, success, log) = result
        results.append((key, line, success, statement))
        print "Completed", len(results), "of", total, success

    total = len(funs)

    run_processes(funs, update)

    #for test in tests:
    #    (success, out, err) = run_process(test)
    #    print out
    #print tests
    #for key in modules.keys():
    #    statements = modules[key]
    #    for i in range(len(statements)):
    #        (line, statement) = statements[i]
    #        print "Trying line", line, statement
    #        (success, out, err) = run_process(lambda: mutate_and_test(key, i))
    #        results.append((key, line, success, statement))
    #        print "Complete line", line, "of", total, success
    return results



def process_results(results):
    files = {}
    for key, group in groupby(results, lambda x: x[0]):
        files[key] = list(group)
    print " "
    print files


def main():
    # Ensure there is at least one argument
    if len(sys.argv) == 1:
        print "Syntax is `linedrop pattern args`"
        sys.exit(1)

    # Assume the first parameter is a regex pattern
    pattern = sys.argv[1]
    print "Using module pattern:", pattern

    # Patch out the pattern from sys.args as the test runners use sys.args.
    # They will not be execting a pattern as the first parameter.
    sys.argv = sys.argv[:1] + sys.argv[2:]

    print "Starting statement discovery."
    ((success, modules), out, err) = run_process(lambda: get_modules(pattern))

    # Ensure the tests passed
    if not success:
        print "Tests failed during discovery. Exiting."
        sys.exit(2)

    print "Discovery complete, tests pass."


    results = run_fixture(modules)
    for result in results:
        print result

    process_results(results)

def collect():
    if len(sys.argv) == 1:
        print "Syntax is `linedrop pattern args`"
        return
    pattern = sys.argv[1]
    sys.argv = sys.argv[:1] + sys.argv[2:]
    (success, modules) = get_modules(pattern)
    for k, v in modules.iteritems():
        for (line, operation) in v:
            print k, line, operation

    total = sum([len(v) for v in modules.values()])

    print ""
    print "Using module pattern:", pattern
    print "Tests were successful:", success
    print "Total statements to test:", total
    print ""

if __name__ == "__main__":
    collect()
