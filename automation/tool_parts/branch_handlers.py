from collections import OrderedDict

from .io import *
from .lib import *
from . import modules


class GenBranch:
    def __init__(self):
        arch = select_arch()
        self.arch = rget(modules, 'arch_' + arch)
        self.mod_list = mod_list(self.arch, 'mod_')

        try:
            self.gen = rget(self.arch, 'Generator', 'Generator')()
        except AttributeError:
            raise InvalidArgument('Arch does not support generating')

    def _get_module(self, module):
        return rget(self.arch, 'mod_' + module, 'Module')

    def _select_module(self):
        name = select(self.mod_list, tooltip='Modules')
        return self._get_module(name)()

    def dispatch_cmd(self):
        dispatcher = OrderedDict([
            ('append a module', self.add_mod),
            ('preview a module', self.preview_mod),
            ('build assembly', self.build),
            ('show modules so far', self.show_mods),
            ('clear selections', self.reset_mods)
        ])

        while True:
            opt = select(list(dispatcher.keys()))
            dispatcher[opt]()

    def add_mod(self):
        mod = self._select_module()

        for pkey, pval in mod.param_template().items():
            validator = mod.get_validator(pkey)
            value = input_field(
                pval,
                tooltip='Parameter \'{}\''.format(pkey.replace('_', ' ')),
                validator=validator
            )
            mod.set_param(pkey, value)

        self.gen.append_module(mod)

    def preview_mod(self):
        mod = self._select_module()

        print(mod.inspect(), end='')

    def build(self):
        shellcode = self.gen.build()
        print(shellcode)

        proceed_prompt('Continue to export')

    def show_mods(self):
        print('Modules so far: ')
        for num, mod in enumerate(self.gen.modules):
            print('    {}. {}'.format(num + 1, mod))

    def reset_mods(self):
        if affirm_prompt('Are you sure'):
            self.gen.clear()
            print('done')

