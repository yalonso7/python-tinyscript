#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Common help utility functions.

"""

__author__ = "Alexandre D'Hondt"
__version__ = "1.0"
__copyright__ = "AGPLv3 (http://www.gnu.org/licenses/agpl.html)"
__all__ = ["bin2int", "bin2txt", "int2bin", "txt2bin",
           "is_bin", "is_str", "is_lst"]


from six import string_types


bin2int = lambda b: int("0b" + b, 2)
bin2txt = lambda b: ''.join(chr(bin2int(''.join(map(str, b[i:i+8])))) \
                    for i in range(0, len(b), 8))
int2bin = lambda i, n=None: ("{}" if n is None else "{:0>" + str(n) + "}") \
                            .format(bin(i)[2:])
txt2bin = lambda t: ''.join(map(lambda c: "{:0>8}".format(bin(ord(c))[2:]), t))

is_str = lambda s: isinstance(s, string_types)
is_bin = lambda b: all(str(_) in "01" for _ in b)
is_lst = lambda l: isinstance(l, (list, tuple))