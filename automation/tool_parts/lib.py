class InvalidArgument(Exception):
    def __init__(self, msg):
        self.msg = msg


def bytes_to_string(data):
    return ''.join('\\x{:02x}'.format(b) for b in data)


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
