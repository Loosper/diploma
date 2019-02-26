import socket

from .ArchModule import Amd64Module


class Module(Amd64Module):
    def __init__(self):
        super().__init__(name='Sys_connect')

    @staticmethod
    def get_data():
        return (
            'sockaddr:\n'
            '    #AF_INET\n'
            '    .byte 2\n'
            '    .byte 0xff\n'
            '    .word {port}\n'
            '    .long 0xffffffff\n'
            '    .byte {}\n'
            '    .byte {}\n'
            '    .byte {}\n'
            '    .byte {}\n'
        )


    def build_data(self):
        port = socket.htons(self.params['port'])
        code = self.get_data()
        ip = self.params['host_ip'].split('.')

        return code.format(*ip, port=port)

    @staticmethod
    def get_code():
        return (
            '    # connect(fd, &sockaddr, 16)\n'
            # '    # move the socket to first argument\n'
            # '    movl %eax, %edi\n'
            '    # sys_connect\n'
            '    xorl %eax, %eax\n'
            '    movb $42, %al\n'
            '    leaq sockaddr(%rip), %rsi\n'
            '    xorl %edx, %edx\n'
            '    # put zeroes in sockaddr\n'
            '    movq %rsi, %r8\n'
            '    inc %r8\n'
            '    movb %dl, (%r8)\n'
            '    addq $3, %r8\n'
            '    movl %edx, (%r8)\n'
            '    # sizof(struct sockaddr)\n'
            '    movb $16, %dl\n'
            '    syscall\n'
            '    # at this point rax could be -111 (connection refused)\n\n'
        )

    @staticmethod
    def param_template():
        return {'port': 10001, 'host_ip': '127.0.0.1'}
