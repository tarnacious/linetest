from mutation.transformer import Transformer
from mutation.load_module import load_module


class CollectStatements(object):
    def __init__(self):
        self.modules = {}

    def find_module(self, module_name, package_path):
        #return self
        # TODO: object level regex
        if module_name.startswith("factorial"):
            return self
        if module_name.startswith("sample"):
            return self

    def collect_statements(self, module_name, ast):
        transformer = Transformer()
        transformer.visit(ast)
        self.modules[module_name] = transformer.items
        return ast

    def load_module(self, module_name):
        mymodule = load_module(module_name, self.collect_statements)
        mymodule.__loader__ = self
        return mymodule
