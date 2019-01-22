from ..BaseModule import BaseModule


class Amd64Module(BaseModule):
    def __init__(self, name):
        super().__init__(name=name, arch='amd64')
