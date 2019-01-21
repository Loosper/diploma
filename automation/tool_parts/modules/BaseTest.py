import re

from ..lib import InvalidArgument, shellcode_validator
from .ContainerLibrary import Container

class BaseTest(Container):
    def __init__(self, code, archs, name):
        self.validate_shellcode = self._validate_shellcode
        self.archs = archs
        # WARNING: escape curly braces!!!
        self.code = code
        self.name = name

        super().__init__()

    def build(self):
        for key, value in self.params.items():
            if value is None:
                raise InvalidArgument(f'{key} is missing')

        return self.code.format(**self.params)

    def inspect(self):
        return self.code
