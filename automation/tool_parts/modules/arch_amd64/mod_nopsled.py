from ..BaseModule import BaseModule


class Module(BaseModule):
    def __init__(self, nnops=1):
        code = 'nopsled:\n'
        code += '    nop\n' * nnops

        super().__init__(
            name='nopsled', arch='amd64',
            code=code
        )
