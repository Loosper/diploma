import subprocess
import re


tmp_file = '/tmp/elffile'
obj_file = '/tmp/out'

objfile_map = {
    'amd64': ['i386:x86-64', 'elf64-x86-64'],
    'x86': ['i386', 'elf32-i386']
}

def disassemble(shellcode, arch):
    arch, elf = objfile_map[arch]
    # parse from \x12 style encoding and store in bytearray to preserve endinanness
    parsed = bytearray(shellcode.encode('ascii').decode('unicode_escape').encode('latin-1'))

    with open(tmp_file, 'bw') as file:
        file.write(parsed)

    subprocess.run([
        'objcopy',
        '-I', 'binary',
        '-O', elf,
        '-B', arch,
        '--set-section-flags', '.data=code', '--rename-section', '.data=.text', '-w', '-N', '*',
        tmp_file, obj_file
    ])

    disasm = subprocess.run(['objdump', '-d', obj_file], capture_output=True)
    ins = re.findall(r'\t[\S ]+\n', disasm.stdout.decode('ascii'))
    ins = [a.strip() for a in ins]
    print('\n'.join(ins))
