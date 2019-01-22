from .ContainerLibrary import Container


class BaseTest(Container):
    def __init__(self, name, archs, code, params={}):
        self.validate_shellcode = self._validate_shellcode
        super().__init__(name=name, code=code, archs=archs, params=params)

    def build(self):
        return self.build_code()
