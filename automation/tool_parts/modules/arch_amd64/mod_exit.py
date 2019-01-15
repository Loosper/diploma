from ..BaseModule import BaseModule


class Module(BaseModule):
    @staticmethod
    def param_template():
        return {'exit_code': 0}

    def __init__(self):
        self.validate_exit_code = self._validate_int

        code = (
            'exit:\n'
            '    # sys_exit\n'
            '    xorl %eax, %eax\n'
            '    movb $60, %al\n'
            '    xorl %edi, %edi\n'
            '    syscall\n'
        )

        super().__init__(name='Sys_exit', arch='amd64', code=code)
