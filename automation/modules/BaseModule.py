class BaseModule:
    # TODO: consider putting the shellcode in a seperate file
    def __init__(self, arch, name, code='', data='', params={}):
        self.name = name
        self.arch = arch
        self.code = code
        self.data = data
        self.params = params

