from .ContainerLibrary import Container


class BaseModule(Container):
    def __init__(self, name, arch, params={}):
        super().__init__(name=name, archs=[arch], params=params)

    def __repr__(self):
        return f'{self.name} {self.params}>'
