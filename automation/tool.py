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
        # TODO: consider using argparse
        self.cmds = {
            'exit': self.exit,
            'help': self.help,
        }
        self.cmds.update(cmds)
        self.tooltip = tooltip

    def __call__(self):
        for args in self.get_input():
            try:
                # this can return things, to be saved in 'global_state'
                # which could itself be modifiable with other commands
                self.cmds[args[0]](args[1:])
            except InvalidArgument as e:
                print(e.msg)
            except KeyError:
                print('Unsupported command :(')
            except StopIteration:
                break

    def get_input(self):
        while True:
            try:
                cmd = input(self.tooltip)
            except EOFError:
                print()
                break

            yield cmd.split()

    def exit(self, args):
        raise StopIteration

    def help(self, args):
        keys = ', '.join(self.cmds.keys())
        print(f'Supported commands: {keys}')


class BaseMode(Mode):
    def __init__(self):
        cmds = {
            'asm': self.asm,
            'disasm': self.disasm,
            'gen': lambda args: GenMode(args)(),
            'test': lambda args: TestMode(args)(),
        }

        super().__init__(cmds)

    def asm(self, args):
        if len(args) < 1:
            raise InvalidArgument('Usage: asm [file]')

        assemble(args[0])

    def disasm(self, args):
        if len(args) < 2:
            raise InvalidArgument('Usage: disasm [shellcode] [arch]')

        # TODO: validation
        disassemble(args[0] , args[1])


class GenMode(Mode):
    def __init__(self, args):
        self.archs = [
            arch[5:] for arch in dir(modules)
            if arch.startswith('arch_')
        ]
        cmds = {
            'add': self.add_mod,
            'show': self.show_mods,
            'build': self.build
            # 'test': self.test???
            # or save and have testing be global?
        }

        if len(args) < 1 or args[0] not in self.archs:
            raise InvalidArgument(
                'Supported architectures: {}'.format(self.archs)
            )
        # checked above
        self.arch = rget(modules, 'arch_' + args[0])

        try:
            self.gen = rget(self.arch, 'Generator', 'Generator')()
        except AttributeError:
            raise InvalidArgument('Arch does not support generating')

        super().__init__(cmds, tooltip='>> ')

    def add_mod(self, args):
        if len(args) < 1:
            raise InvalidArgument('add something')

        try:
            mod = rget(self.arch, 'mod_' + args[0], 'Module')()
            self.gen.append_module(mod)
        except AttributeError:
            raise InvalidArgument('Missing')

    def show_mods(self, args):
        mods = ', '.join(map(repr, self.gen.modules))
        print(f'Modules {mods} for arch {self.gen.arch}')

    def build(self, args):
        print(self.gen.build())


if __name__ == '__main__':
    try:
        BaseMode()()
    except KeyboardInterrupt:
        print('bye')
