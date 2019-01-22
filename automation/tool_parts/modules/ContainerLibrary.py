from ..lib import int_validator, shellcode_validator
from ..io import input_field


class Container:
    # TODO: consider putting code/data in a seperate file
    def __init__(self, name, code, archs=[], data='', params={}):
        self.params = {}
        self.name = name
        # WARNING: escape curly braces!!!
        self.code = code
        self.data = data
        # should be list
        self.archs = archs
        # TODO: assert arch is consistent with paltform naming
        # validate_arch(arch)

        for pname, pval in self.param_template().items():
            validator = self._get_validator(pname)

            # externally set value or prompt user
            value = params.get(pname)
            # print(f'{pname}: {value}')
            if value is None:
                value = input_field(
                    default=pval, validator=validator,
                    tooltip='Parameter \'{}\''.format(pname.replace('_', ' '))
                )

            self.params[pname] = value

    @staticmethod
    def _validate_int(num):
        return int_validator(num)

    @staticmethod
    def _validate_all(val):
        return True

    @staticmethod
    def _validate_shellcode(shellcode):
        return shellcode_validator(shellcode)

    # if no validator, everything works
    def _get_validator(self, key):
        return getattr(self, 'validate_' + key, self._validate_all)

    # in case one of them is a list, convert to string
    def inspect(self):
        return ''.join(self.data) + ''.join(self.code)

    def build_code(self):
        return self.code.format(**self.params)

    def build_data(self):
        return self.data.format(**self.params)

    @staticmethod
    def param_template():
        '''return a dict of all parameters the user should be prompted about'''
        raise NotImplementedError
