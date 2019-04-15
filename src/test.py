#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""
Description:
    Make unit test on lazyparser function and method.
"""

import lazyparser as lp
from lazyparser import Function, List, FileType
import unittest


class TestLazyparser(unittest.TestCase):

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
        self.assertRaises(SystemExit, lp.get_type, "(List(vtype=xd))",
                          argument)

    def test_handled_type(self):
        for o in ["s", "m"]:
            assert lp.handled_type(str, o)
            assert lp.handled_type(int, o)
            assert lp.handled_type(bool, o)
            assert lp.handled_type(float, o)
            assert lp.handled_type(Function, o)
            assert lp.handled_type(FileType("w"), o)
            assert lp.handled_type(854, o)
            assert lp.handled_type("blip", o)
            assert not lp.handled_type(sum, o)
        assert lp.handled_type(List)
        assert lp.handled_type(List(size=5, vtype="int"))
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

    def test_message(self):
        arg = lp.Argument("t", 2, int)
        msg = "argument --t: Hello world"
        assert msg == lp.message("Hello  world", arg, type_m=None)
        assert "warning: " + msg == lp.message("Hello  world", arg, type_m="w")
        assert "error: " + msg == lp.message("Hello  world", arg, type_m="e")


