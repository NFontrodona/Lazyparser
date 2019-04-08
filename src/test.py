#!/usr/bin/env python3

# -*- coding: utf-8 -*-

"""
Description:
    Make unit test on lazyparser function and method.
"""

import lazyparser as lp
from lazyparser import Function, List
import unittest


class TestLazyparser(unittest.TestCase):

    def test_handle(self):
        seqs = ["jdbgjdbgt (lol(lol)) (lilou() blup", "g (li) lou()",
                " (blip)-(bloup)"]
        res = [['(lol(lol))'], ["(li)"], ["(blip)", "(bloup)"]]
        for i in range(len(seqs)):
            assert res[i] == lp.handle(seqs[i])

    def test_set_env(self):
        self.assertRaises(SystemExit, lp.set_env, ":param", "", "")
        self.assertRaises(SystemExit, lp.set_env, "", "", "")
        assert lp.set_env("", ":", "") is None
        assert lp.set_env("param", ":", "Keyword") is None

    def test_get_name(self):
        res = ["L", "lo", "LO", "lol", "l"]
        list_name = [["l", "a"], ["l", "L", "lola"], ["l", "L", "lo"],
                     ["l", "L", "lo", "LO"], []]
        for i in range(len(res)):
            assert res[i] == lp.get_name("lola", list_name[i], size=1)

    def test_get_type(self):
        argument = lp.Argument("t", 2, int)
        assert isinstance(int, type(lp.get_type("(int)", argument)))
        assert isinstance(float, type(lp.get_type("(float)", argument)))
        assert isinstance(str, type(lp.get_type("(str)", argument)))
        assert isinstance(str, type(lp.get_type("(string)", argument)))
        assert isinstance(Function, type(lp.get_type("(Function)", argument)))
        assert isinstance(lp.get_type("(List(vtype=int))", argument), List)
        assert isinstance(lp.get_type("(List)", argument), List)
        self.assertRaises(SystemExit, lp.get_type, "(gloubimou)", argument)
        self.assertRaises(SystemExit, lp.get_type, "(List(vtype=xd))",
                          argument)
