from elftools.elf import elffile
import subprocess

def assemble(path):
    output = '/tmp/output.o'
    assembler = ['as', path, '-o', output]
    subprocess.run(assembler)

    with open(output, 'br') as file:
        dec = elffile.ELFFile(file)
        shellcode = dec.get_section_by_name('.text').data()
        print('"{}"'.format(''.join('\\x{:02x}'.format(b) for b in shellcode)))

