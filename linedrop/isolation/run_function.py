import sys
from linedrop.isolation.logger import Logger
import linedrop.main


class RunFunction(object):

    def __init__(self, module, index, line, statement):
        self.module = module
        self.index = index
        self.line = line
        self.statement = statement

    def __call__(self):
        logger = Logger()
        sys.stdout = logger
        sys.stderr = logger
        result = self.run()
        return (self.module,
                self.line,
                self.statement,
                result,
                logger.log)

    def run(self):
        return linedrop.main.mutate_and_test(self.module, self.index)
