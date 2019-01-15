from ..BaseModule import BaseModule


class Module(BaseModule):
    @staticmethod
    def param_template():
        return {
            'nnops': 1
        }

    def __init__(self):
        self.validate_nnops = self._validate_int
        code = ['nopsled:\n', '    nop\n']
        super().__init__(name='nopsled', arch='amd64', code=code)

    def build_code(self):
        return self.code[0] + self.code[1] * int(self.params['nnops'])
