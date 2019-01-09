from ..BaseGenerator import BaseGenerator

class Generator(BaseGenerator):
    def __init__(self):
        super().__init__(arch='amd64')

    def build(self):
        header = (
            '.global _start\n'
            '.text\n'
            '_start:\n'
            '    jmp begin\n'
        )
        data = ''
        code = 'begin:\n'

        for module in self.modules:
            data += module.build_data()
            code += module.build_code()

        final = header + data + code
        return final
