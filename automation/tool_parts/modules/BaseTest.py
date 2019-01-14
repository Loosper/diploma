from ..lib import InvalidArgument

class BaseTest:
    def __init__(self, code, archs, name, params={}):
        self.archs = archs
        self.params = params
        # WARNING: escape curly braces!!!
        self.code = code
        self.name = name

    def __repr__(self):
        return f'<Test {self.name}>'

    def set_param(self, key, value):
        self.params[key] = value

    def clear(self):
        self.params = dict.fromkeys(self.params, None)

    def build(self):
        for key, value in self.params.items():
            if value is None:
                raise InvalidArgument(f'{key} is missing')

        return self.code.format(**self.params)
