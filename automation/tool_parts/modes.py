from .lib import *  # InvalidArgument, rget, mod_list
from . import modules

from elftools.elf import elffile
from elftools.common.exceptions import ELFError
import subprocess
import sys
import os
import re


# TODO: cli option to run a 'script'
# TODO: identation in modules is fucked
# TODO: args validation with a decorator
# TODO: reasonable and consistent error messages - 'usage: cmd [param1] ..' or 'Please do x'
# TODO: usage help - argparse?
# TODO: help can take arguments - cmd to get help. Use docstring?
# TODO: consistent method and command naming
# TODO: global state
# TODO: colours in shell
# TODO: enocders for shellcode
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
        self.archs = mod_list(modules, 'arch_')

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
        cmds = {
            'add': self.add_mod,
            'list': self.list_mods,
            'preview': self.show_mods,
            'build': self.build,
        }
        super().__init__(cmds, tooltip='>> ')

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


    def add_mod(self, args):
        if len(args) < 1:
            raise InvalidArgument('Please specify a module')

        # TODO: print arguments on error
        # figure out a way to parse input and handle without invocation typerrors
        try:
            mod = rget(self.arch, 'mod_' + args[0], 'Module')(*args[1:])
            self.gen.append_module(mod)
        except AttributeError:
            raise InvalidArgument('No such module')
        # WARNING: this may silence valid typererros from the constructor.
        # ex: int('a')
        except TypeError:
            raise InvalidArgument('Unsupported arguments')

    def show_mods(self, args):
        print(f'Modules for arch {self.gen.arch}')
        for mod in map(repr, self.gen.modules):
            print(mod)

    def inspect_mods(self, args):
        pass

    def list_mods(self, args):
        mods = ', '.join(mod_list(self.arch, 'mod_'))
        print(f'Supported modules: {mods}')

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

        super().__init__(cmds, tooltip='?> ')

        self.test = None

    def show_tests(self, args):
        tests = mod_list(modules, 'test_')
        # TODO: consider printing their repr
        print(f'Supported tests: {tests}')

    # TODO: choose at atartup?
    def use_test(self, args):
        if len(args) < 1:
            raise InvalidArgument('Please specify a test')
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


# TODO: these are mostly arch dependent.
class BuildMode(Mode):
    tmp_path = '/tmp/tool/'

    def __init__(self, args):
        cmds = {
            'asm': self.asm,
            'disasm': self.disasm,
            'extract': self.extract,
            'compile': self.compile,
            'link': self.link,
            'gdb': self.gdb,
            'run': self.run,
        }
        super().__init__(cmds, tooltip='>< ')

        if len(args) < 1:
            raise InvalidArgument('Specify an arch')
        if args[0] not in self.archs:
            raise InvalidArgument('Unsuppoted arch')

        self.arch = args[0]
        os.makedirs(self.tmp_path, exist_ok=True)
        self.tester = None

    # TODO: I think objdump is better if it's just a file.
    #  perhaps disassemble just 1 section/function?
    def disasm(self, args):
        if len(args) < 1:
            raise InvalidArgument('Usage: disasm [shellcode]')

        tmp_file = self.tmp_path + 'elffile'
        obj_file = self.tmp_path + 'out'

        objfile_map = {
            'amd64': ['i386:x86-64', 'elf64-x86-64'],
            'x86': ['i386', 'elf32-i386']
        }

        fformat = objfile_map[self.arch]

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
            '-B', self.arch,
            '--set-section-flags', '.data=code', '--rename-section',
            '.data=.text', '-w', '-N', '*',
            tmp_file, obj_file
        ])

        disasm = subprocess.run(['objdump', '-d', obj_file], capture_output=True)
        # NOTE: this is not perfect
        ins = re.findall(r'\t[\S ]+\n', disasm.stdout.decode('ascii'))
        ins = [a.strip() for a in ins]
        print('\n'.join(ins))

    def extract(self, args):
        if len(args) < 1:
            raise InvalidArgument('Please specify a file')

        try:
            with open(args[0], 'br') as file:
                reader = elffile.ELFFile(file)
                shellcode = reader.get_section_by_name('.text').data()
                print('"{}"'.format(
                    ''.join('\\x{:02x}'.format(b) for b in shellcode)
                ))
        except (FileNotFoundError, IsADirectoryError):
            raise InvalidArgument('Invalid path')
        except ELFError:
            raise InvalidArgument('Input not elf file')

    def asm(self, args):
        if len(args) < 1:
            raise InvalidArgument('Usage: asm [input] [output]')

        output = args[1] if len(args) >= 2 else self.tmp_path + 'output.o'
        assembler = ['as', args[0], '-o', output]
        subprocess.run(assembler)
        print(f'saved to "{output}"')

    def compile(self, args):
        if len(args) < 1:
            raise InvalidArgument('Specify a file to compile')

        cmd = ['gcc', '-c', args[0]]
        if len(args) >= 2:
            cmd.extend(['-o', args[1]])

        subprocess.run(cmd)

    def link(self, args):
        if len(args) < 1:
            raise InvalidArgument('Please specify a file')

        cmd = ['ld', args[0]]
        if len(args) >= 2:
            cmd.extend(['-o', args[1]])

        subprocess.run(cmd)

    def run(self, args):
        if len(args) < 1:
            raise InvalidArgument('Specify a program to run')

        subprocess.run(args)

    def gdb(self, args):
        if len(args) < 1:
            raise InvalidArgument('Specify a file to debug')

        subprocess.run(['gdb', '-q', args[0]])

    # try to do everything
    def all_together(self):
        pass


# maybe some tutorials idk
class Wiki(Mode):
    pass
