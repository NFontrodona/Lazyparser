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
        assert lp.groups == {"lol": ["b", "help"]}
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
        self.assertEqual(None, lp.message("Hello  world", arg, type_m="e"))
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

    # def test_parse(self):
    #     lp.set_env(tb=12)

    #     @lp.parse
    #     def multiply(x: int, y: int):
    #         """
    #         Multiply a by b.

    #         :param x: a number x
    #         :param y: a number y
    #         :return: x * y
    #         """
    #         return x * y

    #     sys.argv = [sys.argv[0]]
    #     for word in "-x 7 -y 8".split():
    #         sys.argv.append(word)
    #     res = multiply().main(standalone_mode=True)
    #     assert res == 7 * 8


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
        lp.groups = {"foo": ["lol", "help"]}
        self.assertEqual(arg.get_parser_group(), "foo")
        lp.groups = {"foo": ["lol"]}
        self.assertEqual(arg.get_parser_group(), "foo")


# class TestLazyparser(unittest.TestCase):
#     def test_equal(self):
#         def func(x, y):
#             return x * y

#         parser = lp.Lazyparser(func, {}, {})
#         parser2 = lp.Lazyparser(func, {}, {})
#         assert parser == parser2

#         def func2(x, z):
#             return x * z

#         parser2 = lp.Lazyparser(func2, {}, {})
#         assert parser != parser2

#     def test_init_arg(self):
#         def func(x, y):
#             return x * y

#         parser = lp.Lazyparser(func, {}, {})
#         dic = {
#             "help": lp.Argument("help", "help", str),
#             "x": lp.Argument("x", inspect._empty, inspect._empty),
#             "y": lp.Argument("y", inspect._empty, inspect._empty),
#         }
#         order = ["help", "x", "y"]
#         assert parser.init_args() == (dic, order)
#         lp.help_arg = False
#         parser = lp.Lazyparser(func, {}, {})
#         dic = {
#             "x": lp.Argument("x", inspect._empty, inspect._empty),
#             "y": lp.Argument("y", inspect._empty, inspect._empty),
#         }
#         order = ["x", "y"]
#         assert parser.init_args() == (dic, order)

#         def func(help, y):
#             return help * y

#         parser.func = func
#         self.assertRaises(SystemExit, parser.init_args)

#     def test_description(self):
#         lp.set_env(delim1=":param", delim2=":", hd="", tb=12)

#         def func(x, y):
#             return x * y

#         parser = lp.Lazyparser(func, {}, {})
#         assert parser.description() == ""
#         parser.func.__doc__ = """Multiply x by y

#             Take two number and multiply them.
#             @Keyword
#             :param x: (int) a number x
#             :param y: (int) a number y"""
#         desc = "Multiply x by yTake two number and multiply them.@Keyword"
#         assert parser.description().replace("\n", "") == desc
#         lp.set_env(delim1="", delim2=":", hd="@Keyword", tb=12)
#         desc = """Multiply x by yTake two number and multiply them."""
#         assert parser.description().replace("\n", "") == desc

#     def test_update_type(self):
#         def func(x, y):
#             return x * y

#         parser = lp.Lazyparser(func, {}, {})
#         assert parser.args["x"].type == inspect._empty
#         parser.update_type("x", ["qsfuhg", "srighdo", "()"])
#         assert parser.args["x"].type == inspect._empty
#         parser.update_type("x", ["(int)"])
#         print(parser.args["x"].type)
#         assert parser.args["x"].type == int
#         parser.update_type("x", ["qsfuhg", "srighdo", "(str)", "(float)"])
#         assert parser.args["x"].type == str

#     def test_update_param(self):
#         lp.set_env(tb=12)

#         def func(x, y):
#             return x * y

#         parser = lp.Lazyparser(func, {}, {})
#         parser.func.__doc__ = """Multiply x by y

#             Take two number and multiply them.

#             :param x: (int) a number x
#             :param y: (int) a number y"""
#         assert parser.args["x"].help == "param x"
#         assert parser.args["y"].type == inspect._empty
#         parser.update_param()
#         assert parser.args["x"].help == "a number x"
#         assert parser.args["y"].help == "a number y"
#         assert parser.args["x"].type == int
#         assert parser.args["y"].type == int
#         lp.set_env(delim1="", tb=12)

#         def func(x, y):
#             return x * y

#         parser = lp.Lazyparser(func, {}, {})
#         parser.func.__doc__ = """Multiply x by y

#             Take two number and multiply them.

#             x: (int) a number : x
#             y: (int) a number : y"""
#         parser.update_param()
#         assert parser.args["x"].help == "a number : x"
#         assert parser.args["y"].help == "a number : y"
#         assert parser.args["x"].type == int
#         assert parser.args["y"].type == int

#     def test_set_filled(self):
#         lp.set_env()

#         def func(x):
#             return x * 2

#         parser = lp.Lazyparser(func, {}, {})
#         parser.set_filled(const="lolipop")
#         assert parser.args["x"].const == "$$void$$"
#         parser.args["x"].type = int
#         self.assertRaises(SystemExit, parser.set_filled, const={"x": 7})
#         parser.args["x"].default = 3
#         parser.set_filled(const={"x": 7})
#         assert parser.args["x"].const == 7
#         parser.args["x"].type = float
#         self.assertRaises(SystemExit, parser.set_filled, const={"x": "b"})
#         parser.args["x"].default = "lul"
#         self.assertRaises(SystemExit, parser.set_filled, const={"x": 7})
#         parser.args["x"].default = 6
#         parser.args["x"].type = List
#         self.assertRaises(SystemExit, parser.set_filled, const={"x": "bloup"})
#         self.assertRaises(
#             SystemExit, parser.set_filled, const={"x": (1, 2, 3)}
#         )
#         parser.args["x"].type = FileType
#         self.assertRaises(SystemExit, parser.set_filled, const={"x": "bb"})

#         class Lol:
#             pass

#         parser.args["x"].type = Lol
#         self.assertRaises(SystemExit, parser.set_filled, const={"x": "bb"})
#         parser.args["x"].type = int
#         self.assertRaises(SystemExit, parser.set_filled, const={"x": "foo"})
#         parser.args["x"].default = "bar"
#         self.assertRaises(SystemExit, parser.set_filled, const={"x": 7})

#     def test_set_constrain(self):
#         lp.set_env()

#         def func(x):
#             return x * 2

#         parser = lp.Lazyparser(func, {}, {})
#         assert parser.args["x"].choice is None
#         parser.set_constrain({"x": "file"})
#         assert parser.args["x"].choice == "file"
#         parser.set_constrain({"x": "x > 5"})
#         assert parser.args["x"].choice == " x > 5 "
#         parser.set_constrain({"x": 5})
#         assert parser.args["x"].choice == 5

#     def test_get_order(self):
#         lp.set_groups()
#         lp.set_env()

#         def func(v, w, x, y, z):
#             return v + w + x + y + z

#         parser = lp.Lazyparser(func, {}, {})
#         assert parser.get_order() == parser.order
#         lp.grp_order = ["Foo", "Optional arguments"]
#         self.assertRaises(SystemExit, parser.get_order)
#         lp.groups = {"Foo": ["v", "w", "x"]}
#         lp.lpg_name = {"Foo": "Foo"}
#         parser = lp.Lazyparser(func, {}, {})
#         assert parser.get_order() == ["v", "w", "x", "help", "y", "z"]
