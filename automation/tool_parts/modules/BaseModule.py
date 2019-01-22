from .ContainerLibrary import Container


class BaseModule(Container):
    def __init__(self, name, arch, code, data='', params={}):
        super().__init__(name=name, code=code, data=data, archs=[arch], params=params)

    def __repr__(self):
        return f'{self.name} {self.params}>'
