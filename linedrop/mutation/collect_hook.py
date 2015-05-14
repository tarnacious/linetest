from linedrop.mutation.transformer import Transformer
from linedrop.mutation.load_module import load_module


class CollectStatements(object):
    def __init__(self):
        self.modules = {}

    def find_module(self, module_name, package_path):
        print "Find_module", module_name, package_path

        # Hack to not load sytem libraries as we get lookups for
        # sample.json.re when really we are tring to import re from inside
        # json, from inside sample :(
        if package_path and len(package_path) > 0 and package_path[0].find("python2.7") > 0:
            return None

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
