class InvalidArgument(Exception):
    def __init__(self, msg):
        self.msg = msg


def rget(*args):
    *head, tail = args
    return getattr(head[0] if len(head) == 1 else rget(*head), tail)

def mod_list(module, prefix):
    start = len(prefix)

    return [
        entry[start:] for entry in dir(module)
        if entry.startswith(prefix)
    ]
