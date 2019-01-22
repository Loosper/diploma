from .ContainerLibrary import Container


class BaseTest(Container):
    def __init__(self, name, archs, params={}):
        self.validate_shellcode = self._validate_shellcode
        super().__init__(name=name, archs=archs, params=params)

    # WARNING: escape curly braces!!!
    def build(self):
        return self.build_code()
