from ..BaseGenerator import BaseGenerator

class Generator(BaseGenerator):
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
