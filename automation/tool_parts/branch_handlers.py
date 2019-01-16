import re
import socket
import logging
import os.path
import subprocess
from collections import OrderedDict

from elftools.elf import elffile

from .io import *
from .lib import *
from . import modules


TMP_PATH = '/tmp/shellcode/'
os.makedirs(TMP_PATH, exist_ok=True)


# TODO: should arch be a settable global?
class GenBranch:
    def __init__(self):
        self.arch = select_arch()
        arch_mod = self._get_arch()
        self.mod_list = mod_list(arch_mod, 'mod_')

        try:
            self.gen = rget(arch_mod, 'Generator', 'Generator')()
        except AttributeError:
            raise InvalidArgument('Arch does not support generating')

    # get the module
    def _get_arch(self):
        return rget(modules, 'arch_' + self.arch)

    def _get_module(self, module):
        return rget(self._get_arch(), 'mod_' + module, 'Module')

    def _select_module(self):
        name = select(self.mod_list, tooltip='Modules')
        return self._get_module(name)()

    def dispatch_module(self):
        dispatcher = OrderedDict([
            ('append a module', self.add_mod),
            ('preview a module', self.preview_mod),
            ('build assembly', self.build),
            ('show modules so far', self.show_mods),
            ('clear selections', self.reset_mods)
        ])

        while True:
            opt = select(list(dispatcher.keys()))
            dispatcher[opt]()

    def dispatch_encode(self):
        pass

    def add_mod(self):
        mod = self._select_module()

        for pkey, pval in mod.param_template().items():
            validator = mod.get_validator(pkey)
            value = input_field(
                pval,
                tooltip='Parameter \'{}\''.format(pkey.replace('_', ' ')),
                validator=validator
            )
            mod.set_param(pkey, value)

        self.gen.append_module(mod)

    def preview_mod(self):
        mod = self._select_module()

        print(mod.inspect(), end='')

    def build(self):
        shellcode = self.gen.build()
        asm_path = TMP_PATH + 'shellcode.s'

        print(shellcode)
        proceed_prompt('Continue to export to binary')

        BuildBranch.save(asm_path, shellcode)
        bin_path = BuildBranch.compile(asm_path, self.arch)
        shellcode = BuildBranch.extract(bin_path, self.arch)

        print('Extracted {} bytes'.format(len(shellcode)))
        print(bytes_to_string(shellcode))

    def show_mods(self):
        print('Modules so far: ')
        for num, mod in enumerate(self.gen.modules):
            print('    {}. {}'.format(num + 1, mod))

    def reset_mods(self):
        if affirm_prompt('Are you sure'):
            self.gen.clear()
            print('done')


# REVIEW: could a _C_ test be invalid for a specific arch?
class TestBranch:
    def __init__(self):
        self.arch = select_arch()
        self.test_list = mod_list(modules, 'test_')

    def _select_test(self):
        test = select(self.test_list, tooltip='Tests')
        return rget(modules, 'test_' + test, 'Test')()

    def dispatch_test(self):
        dispatcher = OrderedDict([
            ('use a test', self.use_test),
            ('preview a test', self.preview_test),
        ])

        while True:
            opt = select(list(dispatcher.keys()))
            dispatcher[opt]()

    def dispatch_exit(self):
        dispatcher = OrderedDict([
            ('exit', sys.exit),
            ('try a different test', self.use_test),
        ])

        opt = select(list(dispatcher.keys()))
        dispatcher[opt]()

    def use_test(self):
        test = self._select_test()

        for pkey, pval in test.param_template().items():
            validator = test.get_validator(pkey)
            value = input_field(
                pval,
                tooltip='Parameter \'{}\''.format(pkey.replace('_', ' ')),
                validator=validator
            )
            test.set_param(pkey, value)

        code = test.build()
        code_path = TMP_PATH + 'test.c'

        BuildBranch.save(code_path, code)
        BuildBranch.compile(code_path, self.arch)

        self.dispatch_exit()

    def preview_test(self):
        test = self._select_test()

        print(test.inspect(), end='')


# TODO: compile/decompile for multiple architectures
class BuildBranch:
    # REVIEW: probably useless
    @staticmethod
    def _safe_exec(cmd, **kwargs):
        finished = subprocess.run(cmd, capture_output=True, **kwargs)
        if finished.returncode != 0:
            raise InvalidArgument(finished.stderr)

        return finished

    @staticmethod
    def save(path, data):
        with open(path, 'w' + ('b' if isinstance(data, bytes) else '')) as file:
            file.write(data)

    @staticmethod
    def extract(path, arch):
        with open(path, 'rb') as file:
            reader = elffile.ELFFile(file)
            shellcode = reader.get_section_by_name('.text').data()

        return shellcode

    @classmethod
    def compile(cls, in_path, arch):
        out_path = input_field('a.out', tooltip='Path to save to')
        root = os.path.dirname(out_path)

        if root != '':
            os.makedirs(root, exist_ok=True)

        tmp_path = TMP_PATH + 'objfile.o'
        # seperate so it works with both assembly and c
        gcc = ['gcc', '-fno-stack-protector', '-c', in_path, '-o', tmp_path]
        ld = [
            'ld', '--entry', 'main',
            '-N', '-z', 'execstack',
            tmp_path, '-o', out_path
        ]

        logging.debug(gcc)
        logging.debug(ld)

        cls._safe_exec(gcc)
        cls._safe_exec(ld)

        return out_path

    # TODO: I think objdump is better if it's just a file.
    #  perhaps disassemble just 1 section/function?
    @classmethod
    def disassemble(cls, code, arch):
        in_file = TMP_PATH + 'elffile'
        obj_file = TMP_PATH + 'out'

        objfile_map = {
            'amd64': ['i386:x86-64', 'elf64-x86-64'],
            'x86': ['i386', 'elf32-i386']
        }

        fformat = objfile_map[arch]

        with open(in_file, 'bw') as file:
            file.write(code)

        cls._safe_exec([
            'objcopy',
            '-I', 'binary',
            '-B', fformat[0],
            '-O', fformat[1],
            '--set-section-flags', '.data=code', '--rename-section',
            '.data=.text', '-w', '-N', '*',
            in_file, obj_file
        ])

        disasm = cls._safe_exec(['objdump', '-d', obj_file])
        # NOTE: this is not perfect
        ins = re.findall(r'\t[\S ]+\n', disasm.stdout.decode('ascii'))
        ins = [a.strip() for a in ins]

        return '\n'.join(ins)


class DisassembleBranch:
    def __init__(self):
        self.arch = select_arch()

    def do_disassemble(self):
        shellcode = input_field(
            None, tooltip='Bytecode',
            validator=shellcode_validator
        )

        assembly = BuildBranch.disassemble(string_to_bytes(shellcode), self.arch)

        print(assembly)


class DebugBranch:
    def dispatch(self):
        dispatcher = OrderedDict([
            ('Two\'s complement', self.twos_comp),
            ('htons', self.htons),
            # ('null byte check', self.byte_check),
            ('quit', sys.exit),
        ])

        while True:
            opt = select(list(dispatcher.keys()), tooltip='Utilities')
            dispatcher[opt]()

    def htons(self):
        num = input_field(None, tooltip='short', validator=int_validator)
        print(socket.htons(int(num)))

    # courtesy of https://stackoverflow.com/questions/1604464/twos-complement-in-python
    @staticmethod
    def _twos_comp(val, bits):
        if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
            val = val - (1 << bits)        # compute negative value
        return val

    def twos_comp(self):
        num = input_field(None, tooltip='two\'s complement number', validator=hex_validator)
        num_len = len(num)

        if num.startswith('0x'):
            num_len -= 2
        num_len *= 4

        print(self._twos_comp(int(num, 16), num_len))

    # # check for [null] bytes
    # def byte_check(self):
    #     pass
