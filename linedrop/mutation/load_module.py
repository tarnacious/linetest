import sys
import ast
import imp
from imp import find_module


def get_package(module_name, depth=1):
    parts = module_name.split(".")
    if len(parts) > depth:
        parent = ".".join(parts[:-depth])
        return sys.modules[parent]


def _is_package(_file):
    return _file is None


def _get_name(module_name):
    return module_name.split(".")[::-1][0]


def _get_filename(_file, path):
    if _file:
        return _file.name
    return "%s/__init__.py" % path


def _get_code_string(_file, path):
    if _file:
        return _file.read()
    filename = _get_filename(_file, path)
    with open(filename, "r") as f:
        return f.read()


def load_module(module_name, ast_fn):
    # Immediatly create a new module and update sys.modules in case this module
    # is imported within the module
    mymodule = imp.new_module(module_name)
    sys.modules.setdefault(module_name, mymodule)

    name = _get_name(module_name)
    package = get_package(module_name)
    if package:
        try:
            found = find_module(name, package.__path__)
        except ImportError:
            # It appears that we are expeted to load either:
            #
            #   sample.sample.factorial
            # or
            #   sample.factorial
            #
            # Both expect us to load the same module. For now basically catch
            # InportError in find_module, then try again stripping off the
            # first module. I'm not sure yet how this is supposed to be done.
            package = get_package(module_name, depth=2)
            if package:
                found = find_module(name, package.__path__)
            else:
                found = find_module(name)
    else:
        found = find_module(module_name)

    (_file, pathname, description) = found
    text = _get_code_string(_file, pathname)

    tree = ast.parse(text)

    if ast_fn:
        tree = ast_fn(module_name, tree)

    compiled = compile(tree, filename="<ast>", mode="exec")

    if _is_package(_file):
        mymodule.__path__ = [pathname]

    mymodule.__file__ = _get_filename(_file, pathname)

    # Let caller see this?
    #mymodule.__loader__ = self

    # Not sure when this should be set
    #mymodule.__package__ = module_name

    exec(compiled, mymodule.__dict__)
    return mymodule