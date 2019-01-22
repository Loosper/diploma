from .ContainerLibrary import Container


class BaseEncoder(Container):
    def __init__(self, name, arch, params={}):
        super().__init__(name=name, archs=[arch], params=params)

    def build(self):
        raise NotImplementedError

    def prepare_build(self):
        pass

