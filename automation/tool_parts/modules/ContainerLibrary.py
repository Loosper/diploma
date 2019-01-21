from ..lib import int_validator, shellcode_validator


class Container:
    def __init__(self):
        self.params = self.param_template()

    @staticmethod
    def param_template():
        raise NotImplementedError

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
    def get_validator(self, key):
        return getattr(self, 'validate_' + key, self._validate_all)

    def set_param(self, key, value):
        result = self.get_validator(key)(value)
        if result:
            self.params[key] = value

        return result

    def inspect(self):
        raise NotImplementedError
