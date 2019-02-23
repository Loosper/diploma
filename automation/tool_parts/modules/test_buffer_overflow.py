from .BaseTest import BaseTest


class Test(BaseTest):
    def __init__(self, params={}):
        super().__init__(
            archs=['x86', 'amd64'],
            name='Test buffer overflow', params=params
        )

    @staticmethod
    def get_code():
        return (
            '#include <stdio.h>\n\n'
            'char shellcode[] = "{shellcode}";\n'
            'int i = 0;\n'
            'int main() {{\n'
            '    char buffer[128];\n'
            '    long *ptr = (long *) buffer;\n'
            '    for (i = 0; i < 20; i++) {{\n'
            '        ptr[i] = (long) buffer;\n'
            '    }}\n'
            '    for (i = 0; i < sizeof(shellcode); i++) {{\n'
            '        buffer[i] = shellcode[i];\n'
            '    }}\n'
            '    return 12;\n'
            '}}\n'
        )

    @staticmethod
    def param_template():
        return {'shellcode': None}
