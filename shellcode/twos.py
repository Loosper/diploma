import sys
# https://stackoverflow.com/questions/1604464/twos-complement-in-python :))))))))))))))
def twos_comp(val, bits):
    """compute the 2's complement of int value val"""
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val

print(twos_comp(int(sys.argv[1], 16), 64))

