from .lib import *  # InvalidArgument, rget, mod_list
from . import modules

from elftools.elf import elffile
from elftools.common.exceptions import ELFError

from functools import wraps
import subprocess
import socket
import sys
import os
import re


# TODO: cli option to run a 'script'
# TODO: identation in modules is fucked
# TODO: reasonable and consistent error messages - 'usage: cmd [param1] ..' or 'Please do x'
# TODO: usage help - convey optional arguments
# docstring to explain module?
# TODO: consistent method and command naming
# TODO: colours in shell
# TODO: enocders for shellcode
# TODO: should global_state have 'formatter' objects?
# TODO: save outputs like paths to file to a global


# decorator for simple argument checks
def _assert_args(*arg_msgs, help_msg=''):
    def decorator(method):
        @wraps(method)
        def decorated(self, args):
            n_args = len(args)
            if n_args < len(arg_msgs):
                # print the message for the next missing arg
                raise InvalidArgument(arg_msgs[n_args])

            method(self, args)

        return decorated
    return decorator


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

    # TODO: should this be more explicit to fit general theme
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
        for args in self._get_input():
            if len(args) == 0:
                continue
            try:
                cmd, *args = args
                self._replace_globals(args)
                cmd = self.cmds.get(cmd)
                if cmd:
                    cmd(args)
                else:
                    print('Unsupported command :(')
            except InvalidArgument as e:
                print(e.msg)
            except StopIteration:
                break
            # makeshift debugging
            # except Exception as e:
            #     import traceback
            #     print()
            #     traceback.print_exc()

    @staticmethod
    def _safe_exec(cmd, **kwargs):
        finished = subprocess.run(cmd, capture_output=True, **kwargs)
        if finished.returncode != 0:
            raise InvalidArgument('Program failed\n' + finished.stderr)

        return finished

    def _get_input(self):
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
        """exit this mode"""
        raise StopIteration

    def help(self, args):
        """display help"""
        if len(args) == 0:
            keys = ', '.join([
                key for key in self.cmds.keys()
                if key not in ['exit', 'help']
            ])
            print(f'Supported commands: {keys}')
            print('Use \'help [cmd]\' for help on each one')
        else:
            cmd = self.cmds.get(args[0])
            if cmd is None:
                raise InvalidArgument('Unsupported command')

            print(cmd.__doc__ if cmd.__doc__ is not None else 'No help :(')

    # TODO: pretty print
    def show_globals(self, args):
        """show globally saved resources"""
        print(self.global_state)


class BaseMode(Mode):
    def __init__(self):
        # a simple wrapper that instantiates the class and calls it
        def _(cls):
            @wraps(cls)
            def hacked(args):
                return cls(args)()

            return hacked

        cmds = {
            'gen': _(GenMode),
            'build': _(BuildMode),
            'test': _(TestMode),
            'debug': _(DebugMode),
        }
        super().__init__(cmds)


class GenMode(Mode):
    """Mode for generating shellcode"""
    def __init__(self, args):
        cmds = {
            'add': self.add_mod,
            'list': self.list_mods,
            'preview': self.show_mods,
            'build': self.build,
            'save': self._saver('shellcode'),
            'clear': self.clear,
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

    @_assert_args('Please specify a module')
    def add_mod(self, args):
        """
        add a module to shellcode
        usage: add [modules] [any params]
        """
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
        """show all added modules"""
        print(f'Modules for arch {self.gen.arch}')
        for mod in map(repr, self.gen.modules):
            print(mod)

    def inspect_mods(self, args):
        pass

    def list_mods(self, args):
        """list all supported modules"""
        mods = ', '.join(mod_list(self.arch, 'mod_'))
        print(f'Supported modules: {mods}')

    def build(self, args):
        """combine the modules and generate the shellcode"""
        shellcode = self.gen.build()
        self.global_state['raw_shellcode'] = shellcode
        # TODO: printing on/or saving in separate command?
        print(shellcode)

    def clear(self, args):
        """clear added modules"""
        self.gen.clear_modules()


class TestMode(Mode):
    """Mode for testing shellcode"""
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
        """list all supported tests"""
        tests = mod_list(modules, 'test_')
        # TODO: consider printing their repr
        print(f'Supported tests: {tests}')

    # TODO: choose at atartup?
    @_assert_args('Please specify a test')
    def use_test(self, args):
        """select a test"""
        try:
            self.test = rget(modules, 'test_' + args[0], 'Test')()
        except AttributeError:
            raise InvalidArgument('No such test')

        print(f'Using {repr(self.test)}')

    def show_params(self, args):
        """show selected parameters"""
        msg = 'Parameters:\n' + '\n'.join([
            f'{key}: {value}' for key, value in self.test.params.items()
        ])

        print(msg)

    @_assert_args('Please provide a key', 'Please provide a value')
    def set_param(self, args):
        """set a parameter
        usage: set [key] [value]
        """
        self.test.set_param(args[0], args[1])

    def build(self, args):
        """generate the test"""
        if self.test is None:
            raise InvalidArgument('No test selected')

        program = self.test.build()
        self.global_state['test'] = program
        print(program)

    # def save(self, args):
    #     if len(args) < 1:
    #         raise InvalidArgument('Please specify a path')

    #     with open(args[0], 'w') as file:
    #         file.write(self.global_state['test'])


# TODO: these are mostly arch dependent.
class BuildMode(Mode):
    """Mode for building programs and shellcode"""
    def __init__(self, args):
        cmds = {
            'asm': self.asm,
            'disasm': self.disasm,
            'extract': self.extract,
            'compile': self.compile,
            'link': self.link,
            'run': self.run,
        }
        super().__init__(cmds, tooltip='>< ')

        if len(args) < 1:
            raise InvalidArgument('Supported archs: {}'.format(self.archs))
        if args[0] not in self.archs:
            raise InvalidArgument('Unsuppoted arch')

        self.arch = args[0]
        self.tester = None

    # TODO: I think objdump is better if it's just a file.
    #  perhaps disassemble just 1 section/function?
    @_assert_args('Please give a shellcode')
    def disasm(self, args):
        """disassemble a string of bytes"""
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
        except AttributeError:
            # parse from \x12 style encoding and store in bytearray to preserve endinanness
            parsed = bytearray(
                str(args[0])
                    .encode('ascii')
                    .decode('unicode_escape')
                    .encode('latin-1')
            )

        with open(tmp_file, 'bw') as file:
            file.write(parsed)

        self._safe_exec([
            'objcopy',
            '-I', 'binary',
            '-B', fformat[0],
            '-O', fformat[1],
            '--set-section-flags', '.data=code', '--rename-section',
            '.data=.text', '-w', '-N', '*',
            tmp_file, obj_file
        ])

        disasm = self._safe_exec(['objdump', '-d', obj_file])
        # NOTE: this is not perfect
        ins = re.findall(r'\t[\S ]+\n', disasm.stdout.decode('ascii'))
        ins = [a.strip() for a in ins]
        print('\n'.join(ins))

    @_assert_args('Please specify a file')
    def extract(self, args):
        """extract shellcode from a binary"""
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

    # this can also have an output
    @_assert_args('Please specify an input')
    def asm(self, args):
        """assemble a file
        usage: asm [shellcode] [output]
        """
        if not os.path.exists(args[0]):
            path = self.tmp_path + 'asm_input'
            with open(path, 'w') as file:
                file.write(args[0])
            input = path
        else:
            input = args[0]

        output = args[1] if len(args) >= 2 else self.tmp_path + 'output.o'
        assembler = ['as', input, '-o', output]
        self._safe_exec(assembler)
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
    @_assert_args('Please Specify a file')
    def compile(self, args):
        """compile a program
        usage: compile [program] [output file]
        """
        cmd = ['gcc', '-c', args[0]]
        if len(args) >= 2:
            cmd.extend(['-o', args[1]])

        self._safe_exec(cmd)

    @_assert_args('Please Specify a file')
    def link(self, args):
        """link a program
        usage: link [program] [output file]
        """
        cmd = ['ld', args[0]]
        if len(args) >= 2:
            cmd.extend(['-o', args[1]])

        self._safe_exec(cmd)

    @_assert_args('Please Specify a program')
    def run(self, args):
        """execute a binary"""
        subprocess.run(args)

    # try to do everything
    def all_together(self):
        pass

class DebugMode(Mode):
    """ Mode for debugging compiled programs"""
    # decorator for standard functions?
    # def std_wrapper(self):
    def __init__(self, args):
        cmds = {
            'gdb': self.gdb,
            'run': self.run,
            'twos': self.twos,
            'htons': self.htons,
        }

        super().__init__(cmds=cmds, tooltip='>.< ')

    @_assert_args('Please Specify a file')
    def gdb(self, args):
        """run an executable in gdb"""
        subprocess.run(['gdb', '-q', args[0]])

    @_assert_args('Please Specify a program')
    def run(self, args):
        """execute a binary"""
        subprocess.run(args)

    @_assert_args('Specify a number')
    def htons(self, args):
        """convert a number to network byte order"""
        socket.htons(int(args[0]))

    # courtesy of https://stackoverflow.com/questions/1604464/twos-complement-in-python
    @staticmethod
    def _twos_comp(val, bits):
        """compute the 2's complement of int value val"""
        if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
            val = val - (1 << bits)        # compute negative value
        return val

    @_assert_args('Specify a number')
    def twos(self, args):
        """convert a hex number to its two's complement equivalent"""
        num = args[0]
        if num.startswith('0x'):
            num = num[2:]

        print(self._twos_comp(int(num, 16), len(num)))


# maybe some tutorials idk
class Wiki(Mode):
    pass
