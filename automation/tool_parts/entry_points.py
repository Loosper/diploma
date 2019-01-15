from collections import OrderedDict

from .io import select
from .branch_handlers import *


def dispatch_generate():
    generator = GenBranch()
    generator.dispatch_module()

def dispatch_test():
    tester = TestBranch()
    tester.dispatch_test()


def dispatch_encode():
    print('now encoding')


def main_dispatcher():
    dispatcher = OrderedDict([
        ('generate', dispatch_generate),
        ('test', dispatch_test),
        ('encode', dispatch_encode),
        ('debug', lambda: print('debug')),
        ('disassemble', lambda: print('disassemble'))
    ])

    opt = select(list(dispatcher.keys()))

    dispatcher[opt]()