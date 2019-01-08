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
# docstring to explain module?
# TODO: consistent method and command naming
# TODO: colours in shell
# TODO: enocders for shellcode
# TODO: should global_state have 'formatter' objects?
# TODO: save outputs like paths to file to a global
# TODO: check subprocess commands for errors
class Mode:
    # shared, because mutable. Do not assign
    # TODO: store shellcode/test objects so you can use them directly
    global_state = {}

    def __init__(self, cmds, tooltip='> '):
        # TODO: consider using argparse
        self.cmds = {
            'exit': self.exit,
            'help': self.help,
            'globals': self.show_globals,
        }
        self.cmds.update(cmds)
        self.tooltip = tooltip
        self.archs = mod_list(modules, 'arch_')
        self.tmp_path = '/tmp/tool/'

        os.makedirs(self.tmp_path, exist_ok=True)

    def _replace_globals(self, args):
        for index, arg in enumerate(args):
            if arg.startswith('!'):
                value = self.global_state.get(arg[1:], None)
                if value is not None:
                    args[index] = value
                else:
                    raise InvalidArgument(f'No global {arg[1:]}')

    def _saver(self, key):
        def save(args):
            data = self.global_state.get(key, None)
            if len(args) < 1:
                raise InvalidArgument('Please specify a path')
            if data is None:
                raise InvalidArgument(f'Please make a {key}')

            with open(args[0], 'w') as file:
                file.write(self.global_state[key])

        return save

    # TODO: add at index
    def __call__(self):
        for args in self.get_input():
            try:
                # TODO: this explodes on nothing
                cmd, *args = args

                self._replace_globals(args)
                self.cmds[cmd](args)
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

    # TODO: pretty print
    def show_globals(self, args):
        print(self.global_state)


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
            'save': self._saver('shellcode'),
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
        shellcode = self.gen.build()
        self.global_state['raw_shellcode'] = shellcode
        # TODO: printing on/or saving in separate command?
        print(shellcode)


class TestMode(Mode):
    def __init__(self, args):
        cmds = {
            'list': self.show_tests,
            'show': self.show_params,
            'use': self.use_test,
            'set': self.set_param,
            'build': self.build,
            'save': self._saver('test'),
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
        self.global_state['test'] = program
        print(program)

    def save(self, args):
        if len(args) < 1:
            raise InvalidArgument('Please specify a path')

        with open(args[0], 'w') as file:
            file.write(self.global_state['test'])


# TODO: these are mostly arch dependent.
class BuildMode(Mode):
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
        self.tester = None

    @staticmethod
    def _check_exit_status(proc):
        if proc.returncode != 0:
            raise InvalidArgument('Process failed.')

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

        try:
            # TODO: assert arch
            parsed = args[0].__bytes__()
        except Exception:
            # parse from \x12 style encoding and store in bytearray to preserve endinanness
            parsed = bytearray(
                str(args[0])
                    .encode('ascii')
                    .decode('unicode_escape')
                    .encode('latin-1')
            )

        with open(tmp_file, 'bw') as file:
            file.write(parsed)

        subprocess.run([
            'objcopy',
            '-I', 'binary',
            '-B', fformat[0],
            '-O', fformat[1],
            '--set-section-flags', '.data=code', '--rename-section',
            '.data=.text', '-w', '-N', '*',
            tmp_file, obj_file
        ])

        disasm = subprocess.run(['objdump', '-d', obj_file], capture_output=True)
        self._check_exit_status(disasm)
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
                formatter = BytesFormat(shellcode, self.arch)
                self.global_state['bin_shellcode'] = formatter
                print('"{}"'.format(formatter))
        except (FileNotFoundError, IsADirectoryError):
            raise InvalidArgument('Invalid path')
        except ELFError:
            raise InvalidArgument('Input not elf file')

    def asm(self, args):
        if len(args) < 1:
            raise InvalidArgument('Usage: asm [input] [output]')

        if not os.path.exists(args[0]):
            path = self.tmp_path + 'asm_input'
            with open(path, 'w') as file:
                file.write(args[0])
            input = path
        else:
            input = args[0]

        output = args[1] if len(args) >= 2 else self.tmp_path + 'output.o'
        assembler = ['as', input, '-o', output]
        self._check_exit_status(subprocess.run(assembler))
        print(f'saved to "{output}"')

    # TODO: if its path-like it will blow up as a compiler not as an invalid path
    # @staticmethod
    # def _save_file(func):
    #     def decorated(self, args):
    #         path = self.tmp_path + 'compile_in'
    #         if not os.path.exists(args[0]):
    #             with open(path, 'w') as file:
    #                 file.write(args[0])
    #             args[0] = path

    #         return func(self, args)

    #     return decorated

    # @_save_file
    def compile(self, args):
        if len(args) < 1:
            raise InvalidArgument('Specify a file to compile')

        cmd = ['gcc', '-c', args[0]]
        if len(args) >= 2:
            cmd.extend(['-o', args[1]])

        self._check_exit_status(subprocess.run(cmd))

    def link(self, args):
        if len(args) < 1:
            raise InvalidArgument('Please specify a file')

        cmd = ['ld', args[0]]
        if len(args) >= 2:
            cmd.extend(['-o', args[1]])

        self._check_exit_status(subprocess.run(cmd))

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
