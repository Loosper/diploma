from disassemble import disassemble
from assemble import assemble
import modules

import sys
import os


def finish(args):
    sys.exit()


def asm(args):
    if len(args) < 1:
        print('Usage: asm [file]')
        return
    assemble(args[0])


def disasm(args):
    if len(args) < 2:
        print('Usage: disasm [shellcode] [arch]')
        return
    disassemble(args[0] , args[1])


def gen(args):
    archs = [arch[5:] for arch in dir(modules) if arch.startswith('arch_')]

    if len(args) < 1 or args[0] not in archs:
        print('Supported architectures:')
        print(archs)
        return

    arch = getattr(modules, 'arch_' + args[0])
    funcs = [mod[4:] for mod in dir(arch) if mod.startswith('mod_')]

    print(funcs)

    print(getattr(getattr(arch, 'mod_' + funcs[0]), 'Module'))



all_cmds = {
    'exit': finish,
    'asm': asm,
    'disasm': disasm,
    'gen': gen
}


while True:
    try:
        cmd = input('> ')
    except EOFError:
        break

    args = cmd.split()

    executor = all_cmds.get(args[0])
    if executor:
        executor(args[1:])
    else:
        print('Unsupported command :(')
