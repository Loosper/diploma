from disassemble import disassemble
from assemble import assemble
import modules

import sys
import os

def rget(*args):
    *head, tail = args
    return getattr(head[0] if len(head) == 1 else rget(*head), tail)


class InvalidArgument(Exception):
    def __init__(self, msg):
        self.msg = msg


class Mode:
    def __init__(self, cmds, tooltip='> '):
        self.cmds = cmds
        self.tooltip = tooltip

    def __call__(self):
        for args in self.get_input():
            try:
                self.cmds.get(args[0])(args[1:])
            except InvalidArgument as e:
                print(e.msg)
            except KeyError:
                print('Unsupported command :(')

    def get_input(self):
        while True:
            try:
                cmd = input(self.tooltip)
            except EOFError:
                print()
                break

            yield cmd.split()


class BaseMode(Mode):
    def __init__(self):
        cmds = {
            'exit': self.finish,
            'asm': self.asm,
            'disasm': self.disasm,
            'gen': lambda args: GenMode(args)()
        }

        super().__init__(cmds)

    def finish(self, args):
        sys.exit()

    def asm(self, args):
        if len(args) < 1:
            raise InvalidArgument('Usage: asm [file]')

        assemble(args[0])

    def disasm(self, args):
        if len(args) < 2:
            raise InvalidArgument('Usage: disasm [shellcode] [arch]')

        disassemble(args[0] , args[1])


class GenMode(Mode):
    def __init__(self, args):
        self.archs = [
            arch[5:] for arch in dir(modules)
            if arch.startswith('arch_')
        ]
        cmds = {
            # 'exit': self.finish,
            'add': self.add_mod,
            'build': self.build
        }

        if len(args) < 1 or args[0] not in self.archs:
            raise InvalidArgument(
                'Supported architectures: {}'.format(self.archs)
            )


        self.arch = rget(modules, 'arch_' + args[0])
        self.gen = rget(self.arch, 'Generator', 'Generator')()

        super().__init__(cmds, tooltip='>> ')

    def add_mod(self, args):
        if len(args) < 1:
            raise InvalidArgument('add something')

        try:
            mod = rget(self.arch, 'mod_' + args[0], 'Module')()
            self.gen.append_module(mod)
        except AttributeError:
            raise InvalidArgument('Missing')

    def build(self, args):
        print(self.gen.build())


try:
    BaseMode()()
except KeyboardInterrupt:
    print('bye')
