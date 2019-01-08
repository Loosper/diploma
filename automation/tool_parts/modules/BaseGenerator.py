class BaseGenerator:
    def __init__(self, arch):
        self.arch = arch
        self.modules = []

    def append_module(self, module):
        self.modules.append(module)

    def build(self):
        raise NotImplementedError