from ..BaseEncoder import BaseEncoder

class ArchEncoder(BaseEncoder):
    def __init__(self, name, code, data, params={}):
        super().__init__(name=name, arch='amd64', code=code, data=data, params=params)

    @staticmethod
    def shellcode_transform(shellcode):
        return ', '.join('0x{:02x}'.format(b) for b in shellcode)

    def build(self):
        self.prepare_build()
        header = (
            '.global _start\n'
            '.text\n'
            '_start:\n'
            '    jmp begin\n'
        )
        begin = 'begin:\n'
        trailer = 'jmp shellcode'

        return (
            header + self.build_data() + begin +
            self.build_code() + trailer
        )
