from linedrop.mutation.transformer import Transformer
from linedrop.mutation.load_module import load_module, _find_module, _get_code_string
import re


class CollectStatements(object):
    def __init__(self, pattern):
        self.modules = {}
        self.pattern = pattern
        self.p = re.compile(pattern)

    def find_module(self, module_name, package_path):
        if not self.p.match(module_name):
            return None

        module = _find_module(module_name)
        if module is None:
            return None
        return self
        # Do we need this shit?
        (_file, pathname, description) = module
        if pathname.startswith(self.path):
            return self
        else:
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
