#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Argreparse module assets' tests.

"""
from tinyscript.argreparse import ArgumentParser, HelpFormatter, Namespace, \
                                  SUPPRESS as SUP, _NewSubParsersAction
from utils import *


FIXTURES = {
    '__author__':    "John Doe",
    '__copyright__': "test",
    '__details__':   "test",
    '__doc__':       "test tool",
    '__email__':     "john.doe@example.com",
    '__examples__':  [],
    '__help__':      "an extra message in addition of __doc__",
    '__license__':   "agpl-v3.0",
    '__status__':    "beta",
    '__version__':   "1.2.3",
}


class TestArgreparse(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.argv = sys.argv[1:]  # backup input arguments
    
    @classmethod
    def tearDownClass(cls):
        sys.argv[1:] = cls.argv  # restore input arguments
    
    def setUp(self):
        temp_stdout(self)
        sys.argv[1:] = []
        ArgumentParser.reset()
        self.p = ArgumentParser(FIXTURES)

    def test_dunders(self):
        self.assertIn("test", self.p.description)
        self.assertIn("agpl-v3.0", self.p.description)
        self.assertIn("John Doe", self.p.description)

    def test_positional_arguments(self):
        temp_stdin(self, "input_test")
        self.p.add_argument("test")
        for _ in self.p._sorted_actions():
            self.p._set_arg(_)
        args = self.p.parse_args()
        self.assertEqual(args.test, "input_test")

    def test_optional_arguments(self):
        self.p.add_argument("--opt1")
        sys.argv += ["--opt1", "test"]
        self.p.add_argument("--opt2", action="store_true")
        sys.argv += ["--opt2"]
        self.p.add_argument("-e", dest="ext", action="extend")
        sys.argv += ["-e", "1", "-e", "2", "-e", "3"]
        args = self.p.parse_args()
        self.assertEqual(args.opt1, "test")
        self.assertEqual(args.opt2, True)
        self.assertEqual(args.ext, ["1", "2", "3"])

    def test_fixed_arguments(self):
        p = ArgumentParser({'__examples__': []})
        p.add_argument("-v", "--verb")
        # this will conflict with the previous one and will then be suffixed
        p.add_argument("-v", "--verb", suffix="mode", action="store_true")
        # this argument will simply be ignored
        p.add_argument("-v", "--verb", suffix="mode")
        p.add_argument("--version")
        p.add_argument("--version", prefix="show", action="store_true")
        p.add_argument("--version", cancel=True)
        args = p.parse_args()
        self.assertIs(args.verb, None)
        self.assertFalse(args.verb_mode)
        self.assertIs(args.version, None)
        self.assertFalse(args.show_version)
    
    def test_mutually_exclusive_arguments(self):
        g = self.p.add_mutually_exclusive_group()
        g.add_argument("-a", action="store_true")
        g.add_argument("-b", action="store_true")
        sys.argv[1:] = ["-a", "-b"]
        self.assertRaises(SystemExit, self.p.parse_args)
        sys.argv[1:] = ["-a"]
        args = self.p.parse_args()
        self.assertTrue(args.a)
        self.assertFalse(args.b)
        sys.argv[1:] = ["-b"]
        args = self.p.parse_args()
        self.assertFalse(args.a)
        self.assertTrue(args.b)

    def test_input_common_actions(self):
        sys.argv[1:] = ["-a", "-b", "-c", "-d", "-e", "--fff", "--fff"]
        self.p.add_argument("-a", action="store", nargs="?", const="TEST")
        self.p.add_argument("-b", action="store_const", const="TEST")
        self.p.add_argument("-c", action="store_true")
        self.p.add_argument("-d", action="store_false")
        self.p.add_argument("-e", action="count")
        self.p.add_argument("--fff", action="count")
        self.p.add_argument("-g", default=1, choices=[1, 2])
        self.p.add_argument("-h", action="help", dest=SUP, default=SUP)
        for a in self.p._actions:
            temp_stdin(self, "\n")
            self.p._input_arg(a)
        args = self.p.parse_args()
        self.p.print_help()
        self.assertEqual(args.a, "TEST")
        self.assertEqual(args.b, "TEST")
        self.assertTrue(args.c)
        self.assertFalse(args.d)
        self.assertEqual(args.e, 1)
        self.assertEqual(args.fff, 2)
        self.assertEqual(args.g, 1)

    def test_set_common_actions(self):
        sys.argv[1:] = ["-c"]
        self.p.add_argument("-a", action="store", nargs="?", const="TEST")
        self.p.add_argument("-b", action="store_const", const="TEST")
        self.p.add_argument("-c", action="store_true")
        self.p.add_argument("-d", action="store_false")
        self.p.add_argument("-e", action="count")
        self.p.add_argument("--fff", action="count")
        self.p.add_argument("-h", action="help", dest=SUP, default=SUP)
        ArgumentParser.add_to_config("main", "a", "TEST")
        ArgumentParser.add_to_config("main", "b", "add")
        ArgumentParser.add_to_config("main", "c", "y")
        ArgumentParser.add_to_config("main", "d", "n")
        ArgumentParser.add_to_config("main", "e", "1")
        ArgumentParser.add_to_config("main", "fff", "2")
        for a in self.p._actions:
            self.p._set_arg(a, c=True)
        args = self.p.parse_args()
        self.assertEqual(args.a, "TEST")
        self.assertEqual(args.b, "TEST")
        self.assertTrue(args.c)
        self.assertFalse(args.d)
        self.assertEqual(args.e, 1)
        self.assertEqual(args.fff, 2)
        self.p._config_parsed = True
        self.p.config_args()
        
    def test_subparser_action(self):
        subparsers = self.p.add_subparsers(dest="command")
        test = subparsers.add_parser("subtest", aliases=["test2"], help="test",
                                     parents=[self.p])
        test.add_argument("--test")
        a = self.p._actions[0]
        temp_stdin(self, "\n")
        self.assertRaises(EOFError, self.p._set_arg, a)
        ArgumentParser.add_to_config("main", "command", "subtest")
        ArgumentParser.add_to_config("subtest", "test", "value")
        self.assertRaises(EOFError, self.p._set_arg, a, c=True)
        test._config_parsed = True
        self.p._set_arg(a, c=True)
    
    def test_bad_action(self):
        self.assertRaises(ValueError, self.p.add_argument, "-a",
                          action="does_not_exist")
        self.p.register('action', "does_not_exist", _FakeParserAction)
        self.p.add_argument("-a", dest="test", action="does_not_exist")
        a = list(self.p._filtered_actions("does_not_exist"))[0]
        self.assertRaises(NotImplementedError, self.p._input_arg, a)
        self.assertRaises(NotImplementedError, self.p._set_arg, a, c=True)
        
    def test_reset_args(self):
        subparsers = self.p.add_subparsers(dest="command")
        test = subparsers.add_parser("subtest", help="test", parents=[self.p])
        self.p._reparse_args['sub'].append(test)
        args = self.p._reset_args()
        self.assertNotIn(test, self.p._reparse_args['sub'])
    
    def test_parser_error(self):
        self.p.add_argument("test")
        self.assertRaises(SystemExit, self.p.parse_args)
    
    def test_parser_subparsers(self):
        subparsers = self.p.add_subparsers(dest="command")
        test = subparsers.add_parser("subtest", help="test", parents=[self.p])
        test.add_argument("--test", dest="verbose")
        if PYTHON3:
            args = self.p.parse_args()
        else:
            self.assertRaises(SystemExit, self.p.parse_args)
    
    def test_help_formatter(self):
        self.p.add_argument("--test", default=",".join(["A"]*30), choices=[1],
                            type=list, help="test", note="special argument",
                            dest=SUP)
        self.p.parse_args()
        self.p.print_help()
        self.p.print_extended_help(3)
    
    def test_namespace(self):
        subparsers = self.p.add_subparsers(dest="command")
        test = subparsers.add_parser("subtest", help="test", parents=[self.p])
        test.add_argument("--test")
        ns = Namespace(self.p)
        setattr(ns, "_hidden", "hidden")
        setattr(ns, "name", "shown")
        setattr(ns, "command", "subtest")
        self.assertEqual(ns._hidden, "hidden")
        self.assertNotIn("hidden", str(ns))
        self.assertEqual(ns.name, "shown")
        self.assertIn("shown", str(ns))
        self.assertEqual(ns._collisions, {})
        o = self.p._config.options("main")
        self.assertIn("_hidden", o)
        self.assertIn("name", o)
        self.assertNotIn("_collisions", o)
        self.assertIs(ns.get("does_not_exist"), None)
    
    def test_custom_constants(self):
        f = {k: v for k, v in FIXTURES.items()}
        for fn, fmt, val in [
                ("test.py", "acronym", "TEST"),
                ("this-is_a_test.py", "acronym", "TIAT"),
                ("this_is-a_test.py", "as_is", "this_is-a_test"),
                ("this-is-a-test.py", "slugified", "ThisIsATest"),
            ]:
            f['__file__'] = fn
            f['SCRIPTNAME_FORMAT'] = fmt
            p = ArgumentParser(f)
            self.assertEqual(p.description.split()[0], val)
        f['SCRIPTNAME_FORMAT'] = "does_not_exist"
        self.assertRaises(ValueError, ArgumentParser, f)
