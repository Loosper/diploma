class BaseModule:
    # TODO: consider putting the shellcode in a seperate file
    def __init__(self, arch, name, code='', data=''):
        self.name = name
        self.arch = arch
        self.code = code
        self.data = data
        self.params = self.param_template()

        # assert self.arch is valid

    def __repr__(self):
        # should i show params?
        return f'{self.name} {self.params}>'

    @staticmethod
    def _validate_int(num):
        try:
            int(num)
        except ValueError:
            return False
        return True

    @staticmethod
    def _validate_all(val):
        return True

    @staticmethod
    def param_template():
        raise NotImplementedError

    # if no validator, everything works
    def get_validator(self, key):
        return getattr(self, 'validate_' + key, self._validate_all)

    def set_param(self, key, value):
        result = getattr(self, 'validate_' + key)(value)
        if result:
            self.params[key] = value

        return result

    def build_code(self):
        return self.code.format(**self.params)

    def build_data(self):
        return self.data.format(**self.params)

    # in case one of them is a list, convert to string
    def inspect(self):
        return ''.join(self.data) + ''.join(self.code)
