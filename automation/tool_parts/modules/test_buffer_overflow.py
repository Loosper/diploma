from .BaseTest import BaseTest


class Test(BaseTest):
    def __init__(self, params={}):
        super().__init__(
            archs=['x86', 'amd64'],
            name='buffer overflow', params=params
        )

    @staticmethod
    def get_code():
        return (
            'char shellcode[] = "{shellcode}";\n\n\n'
            'int main() {{\n'
            '    long *ret;\n\n'
            '    ret = ((long *) &ret) + 2;\n'
            '    *ret = (long) shellcode;\n\n'
            '    return -1;\n'
            '}}\n'
        )

    @staticmethod
    def param_template():
        return {'shellcode': None}
