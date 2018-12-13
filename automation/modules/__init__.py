from pkgutil import walk_packages
from importlib import import_module

# basically from . import *
[import_module(m.name) for m in walk_packages(path=__path__, prefix=__name__+'.')]
