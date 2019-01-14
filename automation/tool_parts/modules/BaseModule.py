class BaseModule:
    # TODO: consider putting the shellcode in a seperate file
    def __init__(self, arch, name, code='', data='', params={}):
        self.name = name
        self.arch = arch
        self.code = code
        self.data = data
        self.params = params

    def __repr__(self):
        # should i show params?
        return f'<Module {self.name} {self.params}>'

    def build_code(self):
        return self.code.format(**self.params)

    def build_data(self):
        return self.data.format(**self.params)

    # in case one of them is a list, convert to string
    def inspect(self):
        return ''.join(self.data) + ''.join(self.code)
