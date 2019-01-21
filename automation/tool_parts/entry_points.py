from collections import OrderedDict

from .io import select
from .lib import InvalidArgument
from .branch_handlers import *


# def dispatcher(branch):
#     branch().dispatch()


def dispatch_generate():
    generator = GenBranch()
    generator.dispatch_module()

def dispatch_test():
    tester = TestBranch()
    tester.dispatch_test()


def dispatch_encode():
    encoder = EncodeBranch()
    encoder.dispatch_encode()


def dispatch_disassemble():
    disasm = DisassembleBranch()
    disasm.do_disassemble()


def dispatch_debug():
    debugger = DebugBranch()
    debugger.dispatch()


def main_dispatcher():
    dispatcher = OrderedDict([
        ('generate', dispatch_generate),
        ('test', dispatch_test),
        ('encode', dispatch_encode),
        ('debug', dispatch_debug),
        ('disassemble', dispatch_disassemble)
    ])

    # TODO: should ^D mean different things in different contexts?
    try:
        opt = select(list(dispatcher.keys()))
        dispatcher[opt]()
    except (KeyboardInterrupt, EOFError):
        print('\nGoodbye')
    except InvalidArgument as e:
        print('Error: {}'.format(e))
