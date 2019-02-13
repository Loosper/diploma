from .ArchModule import Amd64Module


class Module(Amd64Module):
    def __init__(self):
        self.validate_fd = self._validate_int
        super().__init__(name='Sys_dup2')

    # TODO: this is likely to be used many times
    # '    movb $1, %sil\n'
    # '    xorl %eax, %eax\n'
    # '    movb $33, %al\n'
    # '    syscall\n'
    # this saves 2 zeroing instructions
    @staticmethod
    def get_code():
        return (
            '    # dupd2(fd, 0)\n'
            '    xorl %esi, %esi\n'
            '    xorb %sil, %sil\n'
            '    {}\n'
            '    # sys_dup2\n'
            '    movb $33, %al\n'
            '    syscall\n\n'
        )

    def build_code(self):
        fd = self.params['fd']

        ins = 'xorl %eax, %eax' if fd == 0 else f'movl ${fd}, %eax'
        return self.get_code().format(ins)

    @staticmethod
    def param_template():
        return {'fd': 0}
