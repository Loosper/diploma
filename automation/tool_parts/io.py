import platform
import sys

import click

from tool_parts.lib import *
from tool_parts import modules


# TODO: ^C, ^D
def select(choices, tooltip='Actions', default=None):
    if default is None:
        default = 1
    if isinstance(default, str):
        try:
            default = choices.index(default) + 1
        except ValueError:
            default = 1

    print(tooltip + ': ')
    for index, mode in enumerate(choices):
        print('    {}. {}'.format(index + 1, mode))

    opt = click.prompt(
        'Select', default=default,
        type=click.IntRange(1, len(choices))
    )
    chosen = choices[int(opt) - 1]

    return chosen


def affirm_prompt(message):
    choice = input('{}? [y/n]: '.format(message))

    # yes or just an enter
    if choice == 'y' or choice == '':
        return True
    else:
        return False


# yes or quit
def proceed_prompt(message):
    choice = affirm_prompt(message)

    if not choice:
        sys.exit()

    return choice


def input_field(default, tooltip='', validator=lambda x: True, errmsg='Value out of range'):
    while True:
        # default if empty string (newline)
        val = input(tooltip + ' [{}]: '.format(default)) or default
        if validator(val):
            return val
        else:
            print(errmsg)


def select_arch():
    # TODO: unify prefixes
    archs = mod_list(modules, 'arch_')
    default = platform.machine()

    return select(archs, tooltip='Supported architectures', default=default)
