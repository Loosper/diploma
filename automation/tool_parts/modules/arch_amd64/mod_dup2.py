from .ArchModule import Amd64Module


class Module(Amd64Module):
    def __init__(self):
        self.validate_fd = self._validate_int
        super().__init__(name='Sys_dup2')

    @staticmethod
    def get_code():
        return (
            '    # newfd\n'
            '    xorl %esi, %esi\n'
            '    {}\n'
            '    # sys_dup2\n'
            '    xorl %eax, %eax\n'
            '    movb $33, %al\n'
            '    syscall\n\n'
        )

    def build_code(self):
        fd = self.params['fd']

        ins = '' if fd == 0 else f'movb ${fd}, %sil'
        return self.get_code().format(ins)

    @staticmethod
    def param_template():
        return {'fd': 0}
