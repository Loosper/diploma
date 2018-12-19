from ..BaseGenerator import BaseGenerator

class Generator(BaseGenerator):
    def __init__(self):
        super().__init__(arch='amd64')

    def build(self):
        header = '''
        .global _start
        .text
        _start:
            jmp begin
        '''
        data = ''
        code = 'begin:\n'
        params = {}

        for module in self.modules:
            data += module.data
            code += module.code
            params.update(module.params)

        final = header + data + code
        return final.format(**params)
