from ..lib import int_validator, shellcode_validator
from ..io import input_field


class Container:
    # TODO: consider putting code/data in a seperate file
    def __init__(self, name, archs=[], params={}):
        self.params = {}
        self.name = name
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

    @staticmethod
    def get_data():
        return ''

    # WARNING: escape curly braces!!!
    @staticmethod
    def get_code():
        return ''

    def build_data(self):
        return self.get_data().format(**self.params)

    def build_code(self):
        return self.get_code().format(**self.params)

    @classmethod
    def inspect(cls):
        # in case one of them is a list, convert to string
        return ''.join(cls.get_data()) + ''.join(cls.get_code())

    @staticmethod
    def param_template():
        '''return a dict of all parameters the user should be prompted about'''
        return {}
