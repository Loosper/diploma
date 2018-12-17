from .BaseTest import BaseTest


class Test(BaseTest):
    def __init__(self):
        params = {'shellcode': None}
        # WARNING: escape curly braces!!!
        code = '''
            char shellcode[] = "{shellcode}";


            int main() {{
                long *ret;

                ret = ((long *) &ret) + 2;
                *ret = (long) shellcode;

                return -1;
            }}
        '''

        super().__init__(
            archs=['x86', 'amd64'], name='buffer overflow',
            code=code, params=params
        )