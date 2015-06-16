import sys
from linedrop.isolation.logger import Logger
import linedrop.main


class RunFunction(object):

    def __init__(self, module, index):
        self.module = module
        self.index = index

    def __call__(self):
        logger = Logger()
        sys.stdout = logger
        sys.stderr = logger
        result = self.run()
        return (self.module,
                self.index,
                result,
                logger.log)

    def run(self):
        return linedrop.main.mutate_and_test(self.module, self.index)
