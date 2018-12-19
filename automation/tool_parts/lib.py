class InvalidArgument(Exception):
    def __init__(self, msg):
        self.msg = msg


def rget(*args):
    *head, tail = args
    return getattr(head[0] if len(head) == 1 else rget(*head), tail)
