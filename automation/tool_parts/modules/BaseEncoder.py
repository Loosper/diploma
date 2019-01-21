from .ContainerLibrary import Container


class BaseEncoder(Container):
    def __init__(self, arch, name, code='', data=''):
        self.name = name
        self.arch = arch
        self.data = data
        self.code = code

        super().__init__()

    @classmethod
    def validate_shellcode(cls, shellcode):
        if isinstance(shellcode, str):
            return cls._validate_shellcode(shellcode)
        return isinstance(shellcode, bytes)

    def build_code(self):
        return self.code.format(**self.params)

    def build_data(self):
        return self.data.format(**self.params)

    def build(self):
        raise NotImplementedError

    def inspect(self):
        return ''.join(self.code)
