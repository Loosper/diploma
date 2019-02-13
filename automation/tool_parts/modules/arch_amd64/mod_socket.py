from .ArchModule import Amd64Module


class Module(Amd64Module):
    def __init__(self):
        super().__init__(name='Sys_socket')

    @staticmethod
    def get_code():
        return (
            '    # socket(AF_INET, SOCK_STREAM, 0)\n'
            '    # sys_socket\n'
            '    xorl %eax, %eax\n'
            '    movb $41, %al\n'
            '    # AF_INET\n'
            '    xorl %edi, %edi\n'
            '    movb $2, %dil\n'
            '    # SOCK_STREAM\n'
            '    xorl %esi, %esi\n'
            '    movb $1, %sil\n'
            '    # no arguments\n'
            '    xorl %edx, %edx\n'
            '    syscall\n\n'
            '    # move the socket to first argument\n'
            '    movl %eax, %edi\n\n'
        )
