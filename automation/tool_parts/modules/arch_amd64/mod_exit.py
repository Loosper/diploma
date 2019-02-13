from .ArchModule import Amd64Module


class Module(Amd64Module):
    def __init__(self):
        self.validate_exit_code = self._validate_int
        super().__init__(name='Sys_exit')

    @staticmethod
    def get_code():
        return (
            # 'exit:\n'
            '    # sys_exit\n'
            '    xorl %eax, %eax\n'
            '    movb $60, %al\n'
            '    xorl %edi, %edi\n'
            '    syscall\n\n'
        )

    @staticmethod
    def param_template():
        return {'exit_code': 0}
