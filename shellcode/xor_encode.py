import sys

shellcode = sys.argv[1]
shellcode = shellcode.encode('ascii').decode('unicode-escape').encode('latin-1')

xored = []
key = 15

for byte in shellcode:
    xored.append(byte ^ key)

print(f'Number of bytes: {len(xored)}')
xored = ', '.join('0x{:02x}'.format(b) for b in xored)
print(xored)
