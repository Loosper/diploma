from .ContainerLibrary import Container


class BaseEncoder(Container):
    def __init__(self, name, arch, code, data='', params={}):
        super().__init__(name=name, code=code, data=data, archs=[arch], params=params)

    def build(self):
        raise NotImplementedError

    def prepare_build(self):
        pass

