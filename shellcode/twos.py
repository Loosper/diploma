import sys

def twos_comp(val):
    bits = val.bit_length()
    comp = (val ^ (2 ** bits - 1)) + 1
    return -comp

print(twos_comp(int(sys.argv[1], 16)))

