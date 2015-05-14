from linedrop.mutation.transformer import Transformer
from linedrop.mutation.load_module import load_module
import ast


class ModifyModule(object):
    def __init__(self, module_name, index):
        self.module_name = module_name
        self.index = index
        self.current = 0

    def find_module(self, module_name, package_path):
        if module_name == self.module_name:
            return self

    def modify_module(self, module_name, _ast):
        transformer = Transformer(remove_at=self.index)
        transformer.visit(_ast)
        #self.modules[module_name] = transformer.items
        ast.fix_missing_locations(_ast)
        return _ast

    def load_module(self, module_name):
        mymodule = load_module(module_name, self.modify_module)
        mymodule.__loader__ = self
        return mymodule
