from .BaseTest import BaseTest


class Test(BaseTest):
    @staticmethod
    def param_template():
        return {'shellcode': None}

    def __init__(self):
        # WARNING: escape curly braces!!!
        code = (
            'char shellcode[] = "{shellcode}";\n\n\n'
            'int main() {{\n'
            '    long *ret;\n\n'
            '    ret = ((long *) &ret) + 2;\n'
            '    *ret = (long) shellcode;\n\n'
            '    return -1;\n'
            '}}\n'
        )

        super().__init__(
            archs=['x86', 'amd64'],
            name='buffer overflow', code=code
        )
