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


def select_arch():
    archs = mod_list(modules, 'arch_')
    default = platform.machine()

    return select(archs, tooltip='Supported architectures', default=default)


def dispatcher(opts, tooltip='Possible actions', once=False):
    dispatcher = OrderedDict(opts)

    while True:
        opt = select(list(dispatcher.keys()), tooltip=tooltip)
        dispatcher[opt]()

        if once:
            break


def not_implemented():
    print('This is not yet implemented')
    sys.exit()


# BAD NAME
class Base:
    def __init__(self, arch=None):
        self.arch = arch or select_arch()
        self.arch_mod = self._get_arch_module()
        self.shellcode = ''

    def _select_item(self):
        raise NotImplementedError

    # get the module
    def _get_arch_module(self):
        return rget(modules, 'arch_' + self.arch)

    def preview_item(self):
        mod = self._select_item()

        print(mod.inspect(), end='')

class GenBranch(Base):
    def __init__(self, arch=None):
        super().__init__(arch=arch)
        self.mod_list = mod_list(self.arch_mod, 'mod_')
        self.shellcode = None

        try:
            self.gen = rget(self.arch_mod, 'Generator', 'Generator')()
        except AttributeError:
            raise InvalidArgument('Arch does not support generating')

    def _get_module(self, module):
        return rget(self.arch_mod, 'mod_' + module, 'Module')

    def _select_item(self):
        name = select(self.mod_list, tooltip='Modules')
        return self._get_module(name)

    def dispatch_module(self):
        dispatcher([
            ('append a module', self.add_mod),
            ('inspect a module', self.preview_item),
            ('build assembly', self.build_text),
            ('preview current modules', self.show_mods),
            ('clear selections', self.reset_mods)
        ])

    def dispatch_encode(self):
        dispatcher([
            ('test shellcode', self.do_test),
            (
                'encode shellcode',
                EncodeBranch(arch=self.arch, shellcode=self.shellcode).dispatch_encode
            ),
            ('debug tools', DebugBranch().dispatch),
            ('build again', GenBranch(arch=self.arch).dispatch_module),
            ('look at disassembly', self.show_disasm),
            ('save and exit', not_implemented),
            ('exit', sys.exit),
        ], once=True)

    def show_disasm(self):
        # might sound dumb, but this probably should be in the DisasmBranch
        asm = BuildBranch.disassemble(self.shellcode, self.arch)
        print(asm)

    def do_test(self):
        TestBranch(arch=self.arch, shellcode=self.shellcode).dispatch_test()

    def add_mod(self):
        mod = self._select_item()()
        self.gen.append_module(mod)

    def build_text(self):
        shellcode = self.gen.build()
        self.build_binary(shellcode)

    def build_binary(self, shellcode):
        asm_path = TMP_PATH + 'shellcode.s'

        print(shellcode)
        proceed_prompt('Continue to export to binary')

        BuildBranch.save(asm_path, shellcode)
        bin_path = BuildBranch.compile(asm_path, self.arch)
        self.shellcode = BuildBranch.extract(bin_path, self.arch)

        print('Extracted {} bytes'.format(len(self.shellcode)))
        print(bytes_to_string(self.shellcode))

        self.dispatch_encode()

    def show_mods(self):
        print('Modules so far: ')
        for num, mod in enumerate(self.gen.modules):
            print('    {}. {}'.format(num + 1, mod))

    def reset_mods(self):
        if affirm_prompt('Are you sure'):
            self.gen.clear()
            print('done')


class EncodeBranch(Base):
    def __init__(self, arch=None, shellcode=None):
        super().__init__(arch=arch)
        self.item_list = mod_list(self.arch_mod, 'enc_')
        self.shellcode = shellcode

    def _select_item(self):
        enc_name = select(self.item_list, tooltip='Encoders')
        return rget(self.arch_mod, 'enc_' + enc_name, 'Encoder')

    def dispatch_encode(self):
        dispatcher([
            ('use an encoder', self.use_encoder),
            ('preview encoder', self.preview_item),
        ])

    def use_encoder(self):
        enc = self._select_item()(params={'shellcode': self.shellcode})
        shellcode = enc.build()
        GenBranch(arch=self.arch).build_binary(shellcode)


# REVIEW: could a _C_ test be invalid for a specific arch?
class TestBranch(Base):
    def __init__(self, arch=None, shellcode=None):
        super().__init__(arch=arch)
        self.test_list = mod_list(modules, 'test_')
        self.shellcode = bytes_to_string(shellcode) if isinstance(shellcode, bytes) else shellcode

    def _select_item(self):
        test = select(self.test_list, tooltip='Tests')
        return rget(modules, 'test_' + test, 'Test')

    def dispatch_test(self):
        dispatcher([
            ('use a test', self.use_test),
            ('preview a test', self.preview_item),
        ])

    def dispatch_exit(self):
        dispatcher([
            ('exit', sys.exit),
            ('try a different test', self.use_test),
        ], once=True)

    def use_test(self):
        test = self._select_item()(params={'shellcode': self.shellcode})
        code = test.build()
        code_path = TMP_PATH + 'test.c'

        print(code)
        BuildBranch.save(code_path, code)
        BuildBranch.compile(code_path, self.arch)

        self.dispatch_exit()


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
        gcc = ['gcc', '-fno-stack-protector', '-g', '-c', in_path, '-o', tmp_path]
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

    # REVIEW: perhaps disassemble just 1 section/function?
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
        # [0-9abcdefABCDEF]{2}*
        ins = re.findall(r'\t[\S ]+\n', disasm.stdout.decode('ascii'))
        ins = [a.strip() for a in ins]

        return disasm.stdout.decode('ascii')
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
        dispatcher([
            ('two\'s complement', self.twos_comp),
            ('htons', self.htons),
            ('null byte check', not_implemented),
            ('quit', sys.exit),
        ], tooltip='Utilities')

    def htons(self):
        num = input_field(None, tooltip='short', validator=int_validator)
        print(socket.htons(int(num)))

    @staticmethod
    def _twos_comp(val):
        bits = val.bit_length()
        # not the value and add 1 (two's comp)
        comp = (val ^ (2 ** bits - 1)) + 1
        return -comp

    def twos_comp(self):
        num = input_field(None, tooltip='two\'s complement number', validator=hex_validator)

        print(self._twos_comp(int(num, 16)))

    # # check for [null] bytes
    # def byte_check(self):
    #     pass
