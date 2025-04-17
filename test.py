#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""
Description:
    Make unit test on lazyparser function and method.
"""

import inspect
import unittest

import rich_click as click
from rich_click.rich_command import RichCommand

import lazyparser as lp


class TestFunction(unittest.TestCase):
    def test_set_env(self):
        self.assertRaises(SystemExit, lp.set_env, ":param", "", "", 4)
        self.assertRaises(SystemExit, lp.set_env, "", "", "", "4")
        self.assertRaises(SystemExit, lp.set_env, 5, "", "", "4")
        assert lp.set_env("", ":", "", 4) is None
        assert lp.set_env("param", ":", "Keyword", 4) is None

    def test_set_groups(self):
        self.assertRaises(SystemExit, lp.set_groups, {"**": ["b"]})
        lp.set_groups({"lol": ["b", "help"]})
        assert lp.GROUPS == {"lol": ["b", "help"]}
        self.assertRaises(
            SystemExit, lp.set_groups, {"lol": ["b"], "lol*": ["c"]}
        )
        lp.set_groups()

    def test_get_name(self):
        res = ["L", "lo", "LO", "lol", "l"]
        list_name = [
            ["l", "a"],
            ["l", "L", "lola"],
            ["l", "L", "lo"],
            ["l", "L", "lo", "LO"],
            [],
        ]
        for i in range(len(res)):
            assert res[i] == lp.get_name("lola", list_name[i], size=1)

    def test_handled_type(self):
        for o in ["s", "m"]:
            self.assertTrue(lp.handled_type(str, o))
            self.assertTrue(lp.handled_type(int, o))
            self.assertTrue(lp.handled_type(float, o))
            self.assertFalse(lp.handled_type(854, o))
            self.assertFalse(lp.handled_type("blip", o))
            self.assertFalse(lp.handled_type(sum, o))
            self.assertFalse(lp.handled_type(list, o))
        self.assertTrue(lp.handled_type(tuple))
        self.assertTrue(lp.handled_type(bool))
        self.assertFalse(lp.handled_type(click.BOOL))
        self.assertFalse(lp.handled_type(click.Tuple([int, float])))
        self.assertFalse(lp.handled_type(click.Path(exists=True)))

    def test_message(self):
        arg = lp.Argument("t", 2, int)
        self.assertEqual(None, lp.message("Hello  world", arg, type_m=None))
        self.assertRaises(
            SystemExit, lp.message, "Hello  world", arg, type_m="e"
        )
        self.assertEqual(None, lp.message("Hello  world", arg, type_m="w"))

    def test_set_data(self):
        self.assertEqual(lp.set_epilog("uigig"), None)

    def test_init_parser(self):
        lp.set_env(tb=17)

        def func(x, y, z=5, w=7):
            return x * y + z

        doc = """Multiply x by y and add z

                 Take two number and multiply them.

                 :param x: (int) a number x
                 :param y: (int) a number y
                 :param z: (int) a number z"""

        func.__doc__ = doc
        myparser = lp.Lazyparser(func, {})
        parser = lp.init_parser(myparser, func)
        self.assertEqual(type(parser), RichCommand)
        self.assertEqual(
            parser.__doc__.split("\n"),  # type: ignore
            [
                "Multiply x by y and add z",
                "",
                "Take two number and multiply them.",
                "",
            ],
        )

    def test_parse(self):
        lp.set_env(tb=12)
        lp.set_standalone_mode(False)

        @lp.parse()
        def multiply(x: int, y: int):
            """
            Multiply a by b.

            :param x: a number x
            :param y: a number y
            :return: x * y
            """
            return x * y

        import sys

        sys.argv = ["xx", "-x", "7", "-y", "8"]
        self.assertEqual(multiply(), 7 * 8)

    def test_is_click_type(self):
        self.assertFalse(lp.is_click_type(str))
        self.assertFalse(lp.is_click_type(tuple))
        self.assertTrue(lp.is_click_type(click.Path))
        self.assertTrue(lp.is_click_type(click.Path(exists=True)))
        self.assertTrue(lp.is_click_type(click.Path(exists=True)))


class TestArgument(unittest.TestCase):
    def test_get_type(self):
        arg = lp.Argument("lol", 7, int)
        self.assertEqual(arg.get_type(), int)
        arg = lp.Argument("lol", 7, tuple[int, ...])
        self.assertEqual(arg.get_type(), type(tuple[int, ...]))

    def test_set_type(self):
        class Lol:
            pass

        arg = lp.Argument("lol", 7, int)
        self.assertEqual(arg.set_type(int), int)
        self.assertEqual(arg.set_type(inspect._empty), inspect._empty)
        self.assertRaises(SystemExit, arg.set_type, "bloup")
        self.assertRaises(SystemExit, arg.set_type, Lol)
        self.assertRaises(SystemExit, arg.set_type, list)
        arg = lp.Argument("lol", inspect._empty, arg_type=bool)
        arg.set_type(bool)
        self.assertEqual(arg.default, False)
        arg = lp.Argument("lol", (7, "lol"), tuple[int, str])
        self.assertEqual(arg.set_type(tuple[int, str]), tuple[int, str])
        self.assertRaises(SystemExit, arg.set_type, tuple[list, str])

    def test_gfn(self):
        arg = lp.Argument("lol", 7, int)
        self.assertEqual(arg.gfn(), "'[bold cyan]--lol[/bold cyan]'")
        arg.short_name = "l"
        n = (
            "'[bold cyan]--lol[/bold cyan]' "
            + "/ '[bold green]-l[/bold green]'"
        )
        self.assertEqual(arg.gfn(), n)

    def test_click_type(self):
        arg = lp.Argument("lol", 7, bool)
        self.assertEqual(arg.click_type(), click.BOOL)
        arg = lp.Argument("lol", 7, tuple[int, ...])
        self.assertEqual(arg.click_type(), int)
        self.assertEqual(arg.multiple, True)
        arg = lp.Argument("lol", 7, tuple[int, str])
        self.assertEqual(type(arg.click_type()), type(click.Tuple([int, str])))
        self.assertEqual(arg.click_type().types, click.Tuple([int, str]).types)
        self.assertEqual(arg.multiple, False)
        self.assertRaises(SystemExit, lp.Argument, "lol", 7, list)
        arg = lp.Argument("lol", 7, float)
        self.assertEqual(arg.click_type(), float)

    def test_click_narg(self):
        arg = lp.Argument("lol", 7, float)
        self.assertEqual(arg.click_narg(), None)
        arg = lp.Argument("lol", 7, tuple[int, int])
        self.assertEqual(arg.click_narg(), 2)
        arg = lp.Argument("lol", 7, tuple[int, ...])
        self.assertEqual(arg.click_narg(), 1)

    def test_get_parser_group(self):
        arg = lp.Argument("lol", inspect._empty, int)
        self.assertEqual(arg.get_parser_group(), "Required arguments")
        arg = lp.Argument("lol", 6, int)
        self.assertEqual(arg.get_parser_group(), "Optional arguments")
        lp.GROUPS = {"foo": ["lol", "help"]}
        self.assertEqual(arg.get_parser_group(), "foo")
        lp.GROUPS = {"foo": ["lol"]}
        self.assertEqual(arg.get_parser_group(), "foo")


class TestLazyparser(unittest.TestCase):
    def test_equal(self):
        def func(x, y):
            return x * y

        parser = lp.Lazyparser(func, {})
        parser2 = lp.Lazyparser(func, {})
        self.assertTrue(parser == parser2)

        def func2(x, z):
            return x * z

        parser2 = lp.Lazyparser(func2, {})
        self.assertFalse(parser == parser2)

    def test_init_arg(self):
        def func(x, y):
            return x * y

        parser = lp.Lazyparser(func, {})
        dic = {
            "help": lp.Argument("help", "help", str),
            "x": lp.Argument("x", inspect._empty, str),
            "y": lp.Argument("y", inspect._empty, str),
        }
        self.assertEqual(parser.init_args(), dic)

        def func2(help, y):
            return help * y

        parser.func = func2
        self.assertRaises(SystemExit, parser.init_args)

    def test_description(self):
        lp.set_env(delim1=":param", delim2=":", hd="", tb=12)

        def func(x, y):
            return x * y

        parser = lp.Lazyparser(func, {})
        self.assertEqual(parser.description(), "")
        parser.func.__doc__ = """Multiply x by y

            Take two number and multiply them.
            @Keyword
            :param x: (int) a number x
            :param y: (int) a number y"""
        desc = "Multiply x by yTake two number and multiply them.@Keyword"
        self.assertEqual(parser.description().replace("\n", ""), desc)
        lp.set_env(delim1="", delim2=":", hd="@Keyword", tb=12)
        desc = """Multiply x by yTake two number and multiply them."""
        self.assertEqual(parser.description().replace("\n", ""), desc)

    def test_update_param(self):
        lp.set_env(tb=12)

        def func(x, y):
            return x * y

        parser = lp.Lazyparser(func, {})
        parser.func.__doc__ = """Multiply x by y

            Take two number and multiply them.

            :param x: a number x
            :param y: a number y"""
        self.assertEqual(parser.args["x"].help, "param x")
        parser.update_param()
        self.assertEqual(parser.args["x"].help, "a number x")
        self.assertEqual(parser.args["y"].help, "a number y")
        lp.set_env(delim1="", tb=12)

    def test_update_param2(self):
        lp.set_env(tb=12)

        def func(x):
            return x

        parser = lp.Lazyparser(func, {})
        parser.func.__doc__ = """Multiply x by y

            Take one number and return it.

            :param x: a number x with \
            a super long description
            """
        self.assertEqual(parser.args["x"].help, "param x")
        parser.update_param()
        self.assertEqual(
            parser.args["x"].help, "a number x with a super long description"
        )
        lp.set_env(delim1="", tb=12)

    def test_set_constrain(self):
        lp.set_env()

        def func(x: int):
            return x * 2

        parser = lp.Lazyparser(func, {})
        self.assertEqual(parser.args["x"].type, int)
        parser.set_constrain({"x": click.IntRange(5, 10)})
        self.assertEqual(
            type(parser.args["x"].type), type(click.IntRange(5, 10))
        )
        self.assertRaises(SystemExit, parser.set_constrain, {"x": tuple[int]})

    def test_set_version(self):
        lp.set_version("0.2.0")
        self.assertEqual(lp.PROG_VERSION, "0.2.0")
        self.assertEqual(lp.FORBIDDEN, ["help", "h", "version"])
