__version__ = '0.1.1'

import sys


def _index_of(lst, v):
    try:
        return lst.index(v)
    except ValueError:
        return -1


def has_flag(flag: str, argv=sys.argv) -> bool:
    prefix = '' if flag.startswith('-') else ('-' if len(flag) == 1 else '--')
    position = _index_of(argv, prefix + flag)
    terminator_position = _index_of(argv, '--')
    return position != -1 and (terminator_position == -1 or position < terminator_position)
