from disassemble import disassemble
from assemble import assemble
# TODO: restructure, so that everything is in a module and just 'main' is outside it
from modules.errors import InvalidArgument
import modules

from elftools.elf import elffile
import subprocess
import sys
import os
import re


def rget(*args):
    *head, tail = args
    return getattr(head[0] if len(head) == 1 else rget(*head), tail)


# TODO: consistent method and command naming
class Mode:
    # shared, because mutable. Do not assign
    # TODO: store shellcode/test objects so you can use them directly
    global_state = {}

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
            # makeshift debugging
            # except Exception as e:
            #     import traceback
            #     print()
            #     traceback.print_exc()

    def get_input(self):
        while True:
            try:
                cmd = input(self.tooltip)
            except EOFError:
                print()
                break
            # used to clear the screen
            except KeyboardInterrupt:
                print()
                continue

            yield cmd.split()

    def exit(self, args):
        raise StopIteration

    def help(self, args):
        keys = ', '.join([
            key for key in self.cmds.keys()
            if key not in ['exit', 'help']
        ])
        print(f'Supported commands: {keys}')


class BaseMode(Mode):
    def __init__(self):
        def _(cls):
            return lambda args: cls(args)()

        cmds = {
            'gen': _(GenMode),
            'build': _(BuildMode),
            'test': _(TestMode),
        }

        super().__init__(cmds)


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

    # TODO: this is bad. Add a lsit method
    def show_mods(self, args):
        mods = ', '.join(map(repr, self.gen.modules))
        print(f'Modules {mods} for arch {self.gen.arch}')

    def inspect_mods(self, args):
        pass

    def build(self, args):
        print(self.gen.build())


class TestMode(Mode):
    def __init__(self, args):
        cmds = {
            'list': self.show_tests,
            'show': self.show_params,
            'use': self.use_test,
            'set': self.set_param,
            'build': self.build,
        }

        self.test = None

        super().__init__(cmds, tooltip='?> ')

    def show_tests(self, args):
        # TODO: naming and redundancy
        tests = [
            # just the names
            test[5:] for test in dir(modules)
            if test.startswith('test_')
        ]
        # TODO: consider printing their repr
        print(f'Supported tests: {tests}')

    # TODO: choose at atartup?
    def use_test(self, args):
        if len(args) < 1:
            raise InvalidArgument('What should I use?')
        try:
            self.test = rget(modules, 'test_' + args[0], 'Test')()
        except AttributeError:
            raise InvalidArgument('No such test')

        print(f'Using {repr(self.test)}')

    def show_params(self, args):
        msg = 'Parameters:\n' + '\n'.join([
            f'{key}: {value}' for key, value in self.test.params.items()
        ])

        print(msg)

    def set_param(self, args):
        if len(args) != 2:
            raise InvalidArgument('Please provide a key and a value')

        self.test.set_param(args[0], args[1])

    def build(self, args):
        if self.test is None:
            raise InvalidArgument('No test selected')
        program = self.test.build()
        print(program)


class BuildMode(Mode):
    tmp_path = '/tmp/tool/'

    def __init__(self, args):
        os.makedirs(self.tmp_path, exist_ok=True)
        self.tester = None
        cmds = {
            'asm': self.asm,
            'disasm': self.disasm,
        }
        super().__init__(cmds, tooltip='>< ')

    def asm(self, args):
        if len(args) < 1:
            raise InvalidArgument('Usage: asm [file]')

        output = '/tmp/output.o'
        assembler = ['as', args[0], '-o', output]
        subprocess.run(assembler)

        with open(output, 'br') as file:
            dec = elffile.ELFFile(file)
            shellcode = dec.get_section_by_name('.text').data()
            print('"{}"'.format(
                ''.join('\\x{:02x}'.format(b) for b in shellcode)
            ))

    def disasm(self, args):
        # TODO: validation
        if len(args) < 2:
            raise InvalidArgument('Usage: disasm [shellcode] [arch]')

        tmp_file = self.tmp_path + 'elffile'
        obj_file = self.tmp_path + 'out'

        objfile_map = {
            'amd64': ['i386:x86-64', 'elf64-x86-64'],
            'x86': ['i386', 'elf32-i386']
        }

        # def disassemble(shellcode, arch):
        arch, fformat = objfile_map[args[1]]
        # parse from \x12 style encoding and store in bytearray to preserve endinanness
        parsed = bytearray(
            args[0]
                .encode('ascii')
                .decode('unicode_escape')
                .encode('latin-1')
        )

        with open(tmp_file, 'bw') as file:
            file.write(parsed)

        subprocess.run([
            'objcopy',
            '-I', 'binary',
            '-O', fformat,
            '-B', arch,
            '--set-section-flags', '.data=code', '--rename-section', '.data=.text', '-w', '-N', '*',
            tmp_file, obj_file
        ])

        disasm = subprocess.run(['objdump', '-d', obj_file], capture_output=True)
        ins = re.findall(r'\t[\S ]+\n', disasm.stdout.decode('ascii'))
        ins = [a.strip() for a in ins]
        print('\n'.join(ins))

    # def extract(self):
    #     pass

    # def link(self):
    #     pass

    # def run(self):
    #     pass

    # def all_together(self):
    #     self.asm()
    #     self.link()
    #     self.run()



if __name__ == '__main__':
    try:
        BaseMode()()
    except KeyboardInterrupt:
        print('bye')
