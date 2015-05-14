from nose.loader import TestLoader
from nose.core import TextTestRunner
from StringIO import StringIO
import os


def run_tests():
    working_dir = os.path.join(os.getcwd())
    stream = StringIO()
    suites = TestLoader(workingDir=working_dir).loadTestsFromDir("./sample/test_sample")
    runner = TextTestRunner(stream=stream)
    runner = TextTestRunner()
    suites = list(suites)
    results = []
    for suite in suites:
        results.append(runner.run(suite))

    bools = [x.wasSuccessful() for x in results]
    return all(bools)
