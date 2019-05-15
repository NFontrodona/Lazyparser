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

class TestFunction(unittest.TestCase):

    def test_handle(self):
        seqs = ["jdbgjdbgt (lol(lol)) (lilou() blup", "g (li) lou()",
                " (blip)-(bloup)"]
        res = [['(lol(lol))'], ["(li)"], ["(blip)", "(bloup)"]]
        for i in range(len(seqs)):
            assert res[i] == lp.handle(seqs[i])

    def test_set_env(self):
        self.assertRaises(SystemExit, lp.set_env, ":param", "", "", 4)
        self.assertRaises(SystemExit, lp.set_env, "", "", "", 4)
        assert lp.set_env("", ":", "", 4) is None
        assert lp.set_env("param", ":", "Keyword", 4) is None

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
