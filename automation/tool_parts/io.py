import platform
import sys

# import click

from tool_parts.lib import mod_list


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

    if len(choices) == 0:
        print('Internal error: there are no more options')
        sys.exit()

    while True:
        opt = input('Select [{}]: '.format(default))
        # user pressed enter
        if opt == '':
            opt = default
        try:
            opt = int(opt)
            if 1 <= opt <= len(choices):
                break
            else:
                print('Error: integer out of range')
        except ValueError:
            print('Error: invalid integer')

    # opt = click.prompt(
    #     'Select', default=default,
    #     type=click.IntRange(1, len(choices))
    # )
    chosen = choices[int(opt) - 1]

    return chosen


def affirm_prompt(message):
    choice = input('{}? [Y/n]: '.format(message))

    # yes or just an enter
    if choice.lower() == 'y' or choice == '':
        return True
    else:
        return False


# yes or quit
def proceed_prompt(message):
    choice = affirm_prompt(message)

    if not choice:
        sys.exit()

    return choice


def input_field(
    default, tooltip='',
    validator=lambda x: True, errmsg='Value out of range'
):
    while True:
        # default if empty string (newline)
        val = input(
            tooltip +
            (' [{}]'.format(default) if default is not None else '') + ': '
        )
        # if nothing selected, set defualt if available
        if val == '':
            if default is None:
                print('You must input a value')
                continue
            else:
                val = default

        if validator(val):
            return val
        else:
            print(errmsg)
