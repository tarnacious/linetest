class Logger(object):

    log = ""

    def write(self, s):
        self.log = self.log + s

    def flush(self):
        pass
