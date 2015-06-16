import sys
import re
import json
from linedrop.mutation.collect_hook import CollectStatements
from linedrop.mutation.modify_hook import ModifyModule
#from runners.nose_runner import run_tests
from linedrop.runners.pytest_runner import run_tests
from linedrop.isolation.run_process import run_process, run_processes
from linedrop.isolation.run_function import RunFunction
from itertools import groupby


class PyTestRunFunction(RunFunction):

    def run(self):
        hook = ModifyModule(self.module, self.index)
        sys.meta_path.append(hook)
        return run_tests()


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

    mutations = []
    for key in modules.keys():
        statements = modules[key]
        for index in range(len(statements)):
            (line, statement) = statements[index]
            mutations.append((key, index, line, statement))

    def update(result):
        (key, line, statement, success, log) = result
        results.append(result)
        print "Completed", len(results), "of", total, success

    total = len(mutations)
    run_processes(mutations, update, PyTestRunFunction)
    return results


def dump_json(results):
    files = {}
    for key, group in groupby(results, lambda x: x[0]):
        files[key] = list(group)
    filename = "linedrop_results.json"
    print "Writing results to", filename
    with open(filename, "w") as f:
        f.write(json.dumps(files))


def dump_result(results):
    filename = "linedrop_results.txt"
    print "Writing formated results to", filename
    with open(filename, "w") as f:
        for result in results:
            f.write(format_result(*result) + "\n")


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
        print format_result(*result)
    print ""
    dump_result(results)
    dump_json(results)
    print "\nDone."


def format_result(module, line, statement, success, log):
    parts = [pad_module(module), str(line), str(success), strip_statement(statement)]
    return "\t".join(parts)


def pad_module(module):
    return module + " " * (40 - len(module))


def strip_statement(statement):
    return re.match("._ast.([^ ]*) .*", statement).groups()[0]


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
