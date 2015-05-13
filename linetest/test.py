import sys
from mutation.collect_hook import CollectStatements
from mutation.modify_hook import ModifyModule
#from runners.nose_runner import run_tests
from runners.pytest_runner import run_tests
from isolation.run_process import run_process


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


def test():
    hook = ModifyModule("factorial", 0)
    sys.meta_path.append(hook)
    try:
        print "TRY"
        result = run_tests()
        print "CATCH", result
    except:
        print "ERROR"


#(success, modules) = run_process(lambda: get_modules())
(success, modules) = get_modules()

print modules
print modules.keys()

results = run_fixture(modules)
for result in results:
    print result
