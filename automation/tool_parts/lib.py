import re


class InvalidArgument(Exception):
    def __init__(self, msg):
        self.msg = msg


def bytes_to_string(data, sep='', prefix='\\x'):
    return sep.join('{}{:02x}'.format(prefix, b) for b in data)


# parse from \x12 style encoding and store in bytearray to preserve endinanness
def string_to_bytes(data):
    return bytearray(
        data.encode('ascii')
            .decode('unicode_escape')
            .encode('latin-1')
    )

def rget(*args):
    *head, tail = args
    return getattr(head[0] if len(head) == 1 else rget(*head), tail)

def mod_list(module, prefix):
    start = len(prefix)

    return [
        entry[start:] for entry in dir(module)
        if entry.startswith(prefix)
    ]

def validator(func):
    def decorator(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (TypeError, ValueError):
            return False

    return decorator

@validator
def shellcode_validator(shellcode):
    if isinstance(shellcode, bytes):
        return True
    # match anything that is a '\xff' type of escape sequence
    if re.fullmatch(r'(\\x[0-9abcdefABCDEF]{2})+', shellcode):
        return True
    return False

@validator
def int_validator(num):
    if isinstance(num, int):
        return True
    if re.fullmatch(r'-?[0-9]+', num):
        return True
    return False

@validator
def hex_validator(num):
    if re.fullmatch(r'(0x)?[0-9abcdefABCDEF]+', num):
        return True
    return False
