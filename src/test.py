#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""
Description:
    Make unit test on lazyparser function and method.
"""

import lazyparser as lp
from lazyparser import Function, List, FileType
import unittest
import inspect
from argparse import Action

class TestFunction(unittest.TestCase):

    def test_handle(self):
        seqs = ["jdbgjdbgt (lol(lol)) (lilou() blup", "g (li) lou()",
                " (blip)-(bloup)"]
        res = [['(lol(lol))'], ["(li)"], ["(blip)", "(bloup)"]]
        for i in range(len(seqs)):
            assert res[i] == lp.handle(seqs[i])

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
        self.assertRaises(SystemExit, lp.set_groups, {"lol": ["b"], "lol*": ["c"]})
        lp.set_groups()
        print(lp.groups)
        print(lp.lpg_name)
        print(lp.optionals_title)
        print(lp.help_arg)
        print(lp.grp_order)

    def test_get_name(self):
        res = ["L", "lo", "LO", "lol", "l"]
        list_name = [["l", "a"], ["l", "L", "lola"], ["l", "L", "lo"],
                     ["l", "L", "lo", "LO"], []]
        for i in range(len(res)):
            assert res[i] == lp.get_name("lola", list_name[i], size=1)

    def test_get_type(self):
        argument = lp.Argument("t", 2, int)
        type_n = ["(int)", "(float)", "(str)", "(string)", "(Function)"]
        type_r = [int, float, str, str, Function]
        for i in range(len(type_n)):
            res = lp.get_type(type_n[i], argument)
            assert isinstance(type_r[i], type(res[0]))
            assert type_n[i] == res[1]
        assert isinstance(lp.get_type("(List(vtype=int))", argument)[0], List)
        assert isinstance(lp.get_type("(List)", argument)[0], List)
        self.assertRaises(SystemExit, lp.get_type, "(gloubimou)", argument)
        self.assertRaises(SystemExit, lp.get_type, """(List(vtype="xd"))""",
                          argument)

    def test_handled_type(self):
        for o in ["s", "m"]:
            assert lp.handled_type(str, o)
            assert lp.handled_type(int, o)
            assert lp.handled_type(bool, o)
            assert lp.handled_type(float, o)
            assert lp.handled_type(Function, o)
            assert lp.handled_type(FileType("w"), o)
            assert not lp.handled_type(854, o)
            assert not lp.handled_type("blip", o)
            assert not lp.handled_type(sum, o)
        assert lp.handled_type(List)
        assert lp.handled_type(List(size=5, vtype=int))
        assert not lp.handled_type(List, "s")
        assert not lp.handled_type(List(size=5, vtype="int"), "s")

    def test_list(self):
        v = List()
        assert v.size == "+"
        assert v.type == str
        assert v.value is None
        v = List(4, int, [1, 2, 3])
        assert v.size == 4
        assert v.type == int
        assert v.value == [1, 2, 3]
        self.assertRaises(SystemExit, List, 4, int, 7)
        self.assertRaises(SystemExit, List, "22u", int, 7)

    def test_message(self):
        arg = lp.Argument("t", 2, int)
        msg = "argument --t: Hello world"
        assert msg == lp.message("Hello  world", arg, type_m=None)
        assert "warning: " + msg == lp.message("Hello  world", arg, type_m="w")
        assert "error: " + msg == lp.message("Hello  world", arg, type_m="e")

    def test_set_data(self):
        assert lp.set_data("uigig") is None


class TestArgument(unittest.TestCase):

    def test_get_type(self):
        arg = lp.Argument("lol", 7, int)
        assert arg.get_type() == int
        arg = lp.Argument("lol", 7, List(vtype=int))
        assert arg.get_type() == List

    def test_set_type(self):
        class Lol: pass
        arg = lp.Argument("lol", 7, int)
        assert arg.set_type(int) == int
        assert arg.set_type(inspect._empty) == inspect._empty
        self.assertRaises(SystemExit, arg.set_type, "bloup")
        self.assertRaises(SystemExit, arg.set_type, Lol)

    def test_gfn(self):
        arg = lp.Argument("lol", 7, int)
        assert arg.gfn() == "--lol"
        arg.short_name = "l"
        assert arg.gfn() == "-l/--lol"

    def test_argparse_type(self):
        arg = lp.Argument("lol", 7, bool)
        assert arg.argparse_type() == str
        arg = lp.Argument("lol", 7, Function)
        assert arg.argparse_type() == str
        arg = lp.Argument("lol", 7, List(vtype=int))
        assert arg.argparse_type() == int
        arg = lp.Argument("lol", 7, List(vtype=Function))
        assert arg.argparse_type() == str
        arg = lp.Argument("lol", 7, List(vtype=bool))
        assert arg.argparse_type() == str
        arg = lp.Argument("lol", 7, List(vtype=float))
        assert arg.argparse_type() == float
        arg = lp.Argument("lol", 7, float)
        assert arg.argparse_type() == float
        arg = lp.Argument("lol", 7, int)
        assert arg.argparse_type() == int

    def test_argparse_narg(self):
        arg = lp.Argument("lol", 7, float)
        assert arg.argparse_narg() is None
        arg = lp.Argument("lol", 7, List(vtype=(float)))
        assert arg.argparse_narg() == "+"
        arg = lp.Argument("lol", 7, List(5, float))
        assert arg.argparse_narg() == 5

    def test_argparse_metavar(self):
        arg = lp.Argument("lol", 7, FileType("w"))
        assert arg.argparse_metavar() == "File[w]"
        arg = lp.Argument("lol", 7, List(vtype=int))
        assert arg.argparse_metavar() == "List[int]"
        arg = lp.Argument("lol", 7, List(size=5, vtype=int))
        assert arg.argparse_metavar() == "List[5,int]"
        arg = lp.Argument("lol", 7, List(size=5, vtype=FileType("w")))
        assert arg.argparse_metavar() == "List[5,File[w]]"
        arg = lp.Argument("lol", 7, List(size=5, vtype=Function))
        assert arg.argparse_metavar() == "List[5,Func]"
        arg = lp.Argument("lol", 7, List(vtype=FileType("w")))
        assert arg.argparse_metavar() == "List[File[w]]"
        arg = lp.Argument("lol", 7, float)
        assert arg.argparse_metavar() == "float"

    def test_argparse_choice(self):
        arg = lp.Argument("lol", 7, List(size=5, vtype=Function))
        assert arg.argparse_choice() is None
        arg.choice = "test"
        assert arg.argparse_choice() is None
        arg.choice = True
        assert arg.argparse_choice() == "True"
        arg.choice = [1, "foo", True]
        assert arg.argparse_choice() == [1, "foo", 'True']
        arg.choice = [1, "foo", lambda x : x * 2]
        self.assertRaises(SystemExit, arg.argparse_choice)
        arg.choice = lambda x : x * 2
        self.assertRaises(SystemExit, arg.argparse_choice)
        arg.choice = 5
        assert arg.argparse_choice() == 5

    def test_get_parser_group(self):
        arg = lp.Argument("lol", inspect._empty, int)
        assert arg.get_parser_group() == ["__rarg__", lp.required_title]
        arg = lp.Argument("lol", 6, int)
        assert arg.get_parser_group() == ["__parser__", lp.optionals_title]
        lp.groups = {"foo": ["lol", "help"]}
        lp.lpg_name = {"foo": "bar"}
        assert arg.get_parser_group() == ["__parser__", "foo"]
        lp.groups = {"foo": ["lol"]}
        assert arg.get_parser_group() == ["bar", "foo"]


class TestLazyparser(unittest.TestCase):

    def test_equal(self):
        func = lambda x, y: x * y
        parser = lp.Lazyparser(func, {}, {})
        parser2 = lp.Lazyparser(func, {}, {})
        assert parser == parser2
        func = lambda x, z: x * z
        parser2 = lp.Lazyparser(func, {}, {})
        assert parser != parser2

    def test_init_arg(self):
        func = lambda x, y: x * y
        parser = lp.Lazyparser(func, {}, {})
        dic = {"help": lp.Argument("help", "help", str),
               "x": lp.Argument("x", inspect._empty, inspect._empty),
               "y": lp.Argument("y", inspect._empty, inspect._empty)}
        order = ["help", "x", "y"]
        assert parser.init_args() == (dic, order)
        lp.help_arg = False
        parser = lp.Lazyparser(func, {}, {})
        dic = {"x": lp.Argument("x", inspect._empty, inspect._empty),
               "y": lp.Argument("y", inspect._empty, inspect._empty)}
        order = ["x", "y"]
        assert parser.init_args() == (dic, order)
        func = lambda help, y: help * y
        parser.func = func
        self.assertRaises(SystemExit, parser.init_args)

    def test_description(self):
        lp.set_env(delim1=":param", delim2=":", hd="", tb=4)
        func = lambda x, y: x * y
        parser = lp.Lazyparser(func, {}, {})
        assert parser.description() == ""
        parser.func.__doc__ = """Multiply x by y
    
    Take two number and multiply them.
    @Keyword
    :param x: (int) a number x
    :param y: (int) a number y"""
        desc = """Multiply x by y

Take two number and multiply them.
@Keyword"""
        assert  parser.description() == desc
        lp.set_env(delim1="", delim2=":", hd="@Keyword", tb=4)
        desc = """Multiply x by y

Take two number and multiply them."""
        assert  parser.description() == desc

    def test_update_type(self):
        func = lambda x, y: x * y
        parser = lp.Lazyparser(func, {}, {})
        assert parser.args["x"].type == inspect._empty
        parser.update_type("x", ["qsfuhg", "srighdo", "()"])
        assert parser.args["x"].type == inspect._empty
        parser.update_type("x", ["(int)"])
        print(parser.args["x"].type)
        assert parser.args["x"].type == int
        parser.update_type("x", ["qsfuhg", "srighdo", "(str)", "(float)"])
        assert parser.args["x"].type == str

    def test_update_param(self):
        lp.set_env()
        func = lambda x, y: x * y
        parser = lp.Lazyparser(func, {}, {})
        parser.func.__doc__ = """Multiply x by y
    
    Take two number and multiply them.

    :param x: (int) a number x
    :param y: (int) a number y"""
        assert parser.args["x"].help == "param x"
        assert parser.args["y"].type == inspect._empty
        parser.update_param()
        assert parser.args["x"].help == "a number x"
        assert parser.args["y"].help == "a number y"
        assert parser.args["x"].type == int
        assert parser.args["y"].type == int
        lp.set_env(delim1="")
        func = lambda x, y: x * y
        parser = lp.Lazyparser(func, {}, {})
        parser.func.__doc__ = """Multiply x by y

    Take two number and multiply them.

    x: (int) a number : x
    y: (int) a number : y"""
        parser.update_param()
        assert parser.args["x"].help == "a number : x"
        assert parser.args["y"].help == "a number : y"
        assert parser.args["x"].type == int
        assert parser.args["y"].type == int

    def test_set_filled(self):
        lp.set_env()
        func = lambda x: x * 2
        parser = lp.Lazyparser(func, {}, {})
        parser.set_filled(const="lolipop")
        assert parser.args["x"].const == "$$void$$"
        parser.args["x"].type = int
        self.assertRaises(SystemExit, parser.set_filled, const={"x": 7})
        parser.args["x"].default = 3
        parser.set_filled(const={"x": 7})
        assert parser.args["x"].const == 7
        parser.args["x"].type = Function
        self.assertRaises(SystemExit, parser.set_filled,
                          const={"x": lambda x : x* 5})
        self.assertRaises(SystemExit, parser.set_filled,
                          const={"x": "lambda x : x* 5"})
        parser.args["x"].type = List
        self.assertRaises(SystemExit, parser.set_filled,
                          const={"x": "bloup"})
        self.assertRaises(SystemExit, parser.set_filled,
                          const={"x": (1, 2, 3)})
        parser.args["x"].type = FileType
        self.assertRaises(SystemExit, parser.set_filled,
                          const={"x": "bb"})
        class Lol: pass
        parser.args["x"].type = Lol
        self.assertRaises(SystemExit, parser.set_filled,
                          const={"x": "bb"})
        parser.args["x"].type = int
        self.assertRaises(SystemExit, parser.set_filled, const={"x": "foo"})
        parser.args["x"].default = "bar"
        self.assertRaises(SystemExit, parser.set_filled, const={"x": 7})

    def test_set_constrain(self):
        lp.set_env()
        func = lambda x: x * 2
        parser = lp.Lazyparser(func, {}, {})
        assert parser.args["x"].choice is None
        parser.set_constrain({"x": "file"})
        assert parser.args["x"].choice == "file"
        parser.set_constrain({"x": "x > 5"})
        assert parser.args["x"].choice == " x > 5 "
        parser.set_constrain({"x": 5})
        assert parser.args["x"].choice == 5

    def test_get_order(self):
        lp.set_groups()
        lp.set_env()
        func = lambda v, w, x, y, z : v + w + x + y + z
        parser = lp.Lazyparser(func, {}, {})
        assert parser.get_order() == parser.order
        lp.grp_order = ["Foo", "Optional arguments"]
        self.assertRaises(SystemExit, parser.get_order)
        lp.groups = {"Foo": ["v", "w", "x"]}
        lp.lpg_name = {"Foo": "Foo"}
        parser = lp.Lazyparser(func, {}, {})
        assert parser.get_order() == ["v", "w", "x", "help", "y", "z"]


class TestNewFormatter(unittest.TestCase):
    """
    Test New argparse Help Formatter
    """
    def test_init(self):
        fmt = lp.NewFormatter("lol.py")
        assert fmt._width == 120
        assert fmt._max_help_position == 50

    def test_format_args(self):
        action = Action("-a", "a")
        fmt = lp.NewFormatter("lol.py")
        assert fmt._format_args(action, "a") == "a"

    def test_format_action_invocation(self):
        action = Action("d", "a")
        fmt = lp.NewFormatter("lol.py")
        assert fmt._format_action_invocation(action) == "d A"
        action = Action("d", "a", nargs=0)
        assert fmt._format_action_invocation(action) == "d"



