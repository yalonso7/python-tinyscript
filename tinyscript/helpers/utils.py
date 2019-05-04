#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Common utility functions.

"""
import re
import sys
from humanfriendly.terminal import ansi_wrap
from platform import uname
from six import b as six_b, u, StringIO as SIO
from sys import version_info

from .lambdas import is_lambda
from ..__info__ import __author__, __copyright__, __version__


__all__ = __features__ = ["LINUX", "PYTHON3", "WINDOWS", "b", "byteindex",
                          "capture", "iterbytes", "silent", "std_input", "u",
                          "user_input", "Capture"]


LINUX   = uname()[0] == "Linux"
WINDOWS = uname()[0] == "Windows"

PYTHON3      = version_info > (3,)
CHOICE_REGEX = re.compile(r'^\(([a-z0-9])\).*$', re.I)


# see: http://python3porting.com/problems.html
byteindex = lambda d, i=None: d[i] if PYTHON3 else ord(d[i])
iterbytes = lambda d: iter(d) if PYTHON3 else [ord(c) for c in d]


def b(text):
    """
    Overload for six.b function, because the behavior of 'b' in Python2/3 is not
     exactly the same. This makes 'b' behave in Python 3 like in Python 2.
    """
    try:
        return six_b(text)
    except:
        return text


class StringIO(SIO):
    """
    Tuned StringIO class.
    """
    def __str__(self):
        return self.getvalue().strip()
    
    @property
    def text(self):
        return str(self)


class Capture(object):
    """
    Context manager for capturing stdout and stderr.
    """
    def __enter__(self):
        sys.stdout, sys.stderr = StringIO(), StringIO()
        return sys.stdout, sys.stderr
    
    def __exit__(self, *args):
        sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__


def capture(f):
    """
    Decorator for capturing stdout and stderr.
    """
    def _wrapper(*a, **kw):
        with Capture() as (out, err):
            r = f(*a, **kw)
        return r, out.text, err.text
    return _wrapper


def silent(f):
    """
    Decorator for silencing stdout and stderr.
    """
    def _wrapper(*a, **kw):
        with Capture():
            r = f(*a, **kw)
        return r
    return _wrapper


def std_input(prompt="", style=None):
    """
    Very simple Python2/3-compatible input method.
    
    :param prompt:  prompt message
    :param style:   dictionary of ansi_wrap keyword-arguments
    """
    p = ansi_wrap(prompt, **(style or {}))
    try:
        return raw_input(p).strip()
    except NameError:
        return input(p).strip()


def user_input(prompt="", choices=None, default=None, choices_str="",
               required=False):
    """
    Python2/3-compatible input method handling choices and default value.
    
    :param prompt:   prompt message
    :param choices:  list of possible choices or lambda function
    :param default:  default value
    :param required: make non-null user input mandatory
    :return:         handled user input
    """
    if type(choices) in [list, tuple, set]:
        choices = list(map(str, choices))
        choices_str = " {%s}" % (choices_str or \
                                 '|'.join(list(map(str, choices))))
        # consider choices of the form ["(Y)es", "(N)o"] ;
        #  in this case, we want the choices to be ['y', 'n'] for the sake of
        #  simplicity for the user
        m = list(map(lambda x: CHOICE_REGEX.match(x), choices))
        choices = [x.group(1).lower() if x else c for x, c in zip(m, choices)]
        # this way, if using ["Yes", "No"], choices will remain so
        _check = lambda v: v in choices
    elif is_lambda(choices):
        _check = choices
    else:
        _check = lambda v: True
    prompt += "{}{}\n".format(choices_str, [" [{}]".format(default), ""]\
                                           [default is None and required])
    user_input, first = None, True
    while not user_input:
        user_input = std_input(["", prompt][first] + " >> ")
        first = False
        if type(choices) in [list, tuple, set]:
            choices = list(map(lambda x: x.lower(), choices))
            user_input = user_input.lower()
        if user_input == "" and default is not None and _check(default):
            return str(default)
        if user_input != "" and _check(user_input):
            return user_input
        if not required:
            return
