import re

from ..lib import InvalidArgument, string_to_bytes
from .ContainerLibrary import Container

class BaseTest(Container):
    def __init__(self, code, archs, name):
        self.archs = archs
        # WARNING: escape curly braces!!!
        self.code = code
        self.name = name

        super().__init__()

    def __repr__(self):
        return f'<Test {self.name}>'

    @staticmethod
    def _validate_shellcode(shellcode):
        try:
            # match anything that is a '\xff' type of escape sequence
            if re.fullmatch(r'(\\x[0-9abcdef]{2})+', shellcode):
                return True
        except TypeError:
            pass
        return False

    def build(self):
        for key, value in self.params.items():
            if value is None:
                raise InvalidArgument(f'{key} is missing')

        return self.code.format(**self.params)

    def inspect(self):
        return self.code
