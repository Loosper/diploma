from .BaseTest import BaseTest


class Test(BaseTest):
    def __init__(self, params={}):
        super().__init__(
            archs=['x86', 'amd64'],
            name='Return to code', params=params
        )

    @staticmethod
    def get_code():
        return (
            'int main() {{\n'
            '    long *ret;\n\n'
            '    char shellcode[] = "{shellcode}";\n\n\n'
            '    ret = ((long *) &ret) + 2;\n'
            '    *ret = (long) shellcode;\n\n'
            '    return -1;\n'
            '}}\n'
        )

    @staticmethod
    def param_template():
        return {'shellcode': None}
