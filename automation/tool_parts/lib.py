class InvalidArgument(Exception):
    def __init__(self, msg):
        self.msg = msg


class BytesFormat:
    def __init__(self, data, arch):
        self.data = data
        self.arch = arch

    def __repr__(self):
        return '<Binary shellcode>'

    def __bytes__(self):
        return self.data
    def __len__(self):
        return len(self.data)

    def __str__(self):
        return ''.join('\\x{:02x}'.format(b) for b in self.data)


def rget(*args):
    *head, tail = args
    return getattr(head[0] if len(head) == 1 else rget(*head), tail)

def mod_list(module, prefix):
    start = len(prefix)

    return [
        entry[start:] for entry in dir(module)
        if entry.startswith(prefix)
    ]
