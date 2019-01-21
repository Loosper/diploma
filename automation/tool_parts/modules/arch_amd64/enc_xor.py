from .ArchEncoder import ArchEncoder

from ...lib import string_to_bytes

class Encoder(ArchEncoder):
    @staticmethod
    def param_template():
        return {'xor_key': '15', 'shellcode': None}

    def __init__(self):
        data = (
            'key:\n'
            '    .byte {xor_key}\n'
            'shellcode:\n'
            '    .byte {shellcode}\n'
        )
        code = (
            'xor_encoder:\n'
            '    movb key(%rip), %bl\n'
            '    xorw %ax, %ax\n'
            'loop:\n'
            '    leaq shellcode(%rip), %rcx\n'
            '    addq %rax, %rcx\n'
            '    xorb %bl, (%rcx)\n'
            '    inc %ax\n'
            '    cmpw ${shellcode_length}, %ax\n'
            '    jle loop\n'
            '    jmp shellcode\n'
        )

        super().__init__(name='xor encoder', code=code, data=data)

    def build_data(self):
        key = int(self.params['xor_key'])
        xored = []
        # TODO: do this in initialisation or have it passed in bytes
        self.params['shellcode'] = string_to_bytes(self.params['shellcode'])
        for byte in self.params['shellcode']:
            xored.append(byte ^ key)

        xored = ', '.join('0x{:02x}'.format(b) for b in xored)

        return self.data.format(xor_key=key, shellcode=xored)

    def build_code(self):
        # TEMPORARY: data is built before code
        self.code = self.code.format(shellcode_length=len(self.params['shellcode']))
        return super().build_code()
