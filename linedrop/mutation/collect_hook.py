from linedrop.mutation.transformer import Transformer
from linedrop.mutation.load_module import load_module, _find_module, _get_code_string


class CollectStatements(object):
    def __init__(self, path):
        self.modules = {}
        self.path = path

    def find_module(self, module_name, package_path):
        module = _find_module(module_name)
        (_file, pathname, description) = module
        if pathname.startswith(self.path):
            print "HANDLE", module_name, pathname
            return self
        else:
            print "KICK", module_name, pathname
            return None

    def collect_statements(self, module_name, ast):
        transformer = Transformer()
        transformer.visit(ast)
        self.modules[module_name] = transformer.items
        return ast

    def load_module(self, module_name):
        mymodule = load_module(module_name, self.collect_statements)
        mymodule.__loader__ = self
        return mymodule
