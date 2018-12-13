from elftools.elf import elffile
import sys


with open(sys.argv[1], 'br') as file:
    dec = elffile.ELFFile(file)
    shellcode = dec.get_section_by_name('.text').data()
    # print(repr(shellcode))
    print('"{}"'.format(''.join('\\x{:02x}'.format(b) for b in shellcode)))
