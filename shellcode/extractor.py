from elftools.elf import elffile

with open('./a.out', 'br') as file:
    dec = elffile.ELFFile(file)
    shellcode = dec.get_section_by_name('.text').data()
    print("b'{}'".format(''.join('\\x{:02x}'.format(b) for b in shellcode)))
