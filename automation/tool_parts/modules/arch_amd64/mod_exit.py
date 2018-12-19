from ..BaseModule import BaseModule


class Module(BaseModule):
    def __init__(self, code=0):
        params = {'exit_code': code}
        code ='''
        exit:
            # sys_exit
            xorl %eax, %eaxs
            movb $60, %al
            xorl %edi, %edi
            syscall
        '''
        super().__init__(
            name='Sys_exit', arch='amd64',
            code=code, params=params
        )
