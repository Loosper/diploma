from .ArchModule import Amd64Module


class Module(Amd64Module):
    def __init__(self):
        self.validate_nnops = self._validate_int
        super().__init__(name='nopsled')

    @staticmethod
    def get_code():
        return ['nopsled:\n', '    nop\n']

    def build_code(self):
        code = self.get_code()
        return code[0] + code[1] * int(self.params['nnops']) + '\n'

    @staticmethod
    def param_template():
        return {'nnops': 1}
