from ..BaseModule import BaseModule


class Module(BaseModule):
    def __init__(self, code=0):
        params = {'exit_code': code}
        code = (
            'exit:\n'
            '    # sys_exit\n'
            '    xorl %eax, %eax\n'
            '    movb $60, %al\n'
            '    xorl %edi, %edi\n'
            '    syscall\n'
        )

        super().__init__(
            name='Sys_exit', arch='amd64',
            code=code, params=params
        )
