from ..BaseModule import BaseModule


class Module(BaseModule):
    def __init__(self, nnops=1):
        params = {
            'nnops': nnops
        }
        code = ['nopsled:\n', '    nop\n']

        super().__init__(
            name='nopsled', arch='amd64',
            code=code, params=params
        )

    def build_code(self):
        return self.code[0] + self.code[1] * int(self.params['nnops'])
