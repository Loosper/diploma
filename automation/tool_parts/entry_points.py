from collections import OrderedDict

from .io import select
from .branch_handlers import *

def dispatch_generate():
    # arch = select_arch()
    generator = GenBranch()
    generator.dispatch_cmd()
    # generator.add_mod()


def begin_encode():
    print('now encoding')


def main_dispatcher():
    dispatcher = OrderedDict(
        [('generate', dispatch_generate),
        ('test', lambda: print('test')),
        ('encode', begin_encode),
        ('debug', lambda: print('debug')),
        ('disassemble', lambda: print('disassemble'))]
    )

    opt = select(list(dispatcher.keys()))

    dispatcher[opt]()