#!/usr/bin/env python3

# -*- coding utf-8 -*-

"""
Description:
    This script define the lazyparser.
"""

import argparse
import re
import inspect
import functools

type_list = {"(int)": int, "(float)": float, "(string)": str, "(str)": str,
             "(file)": str, "(bool)": bool,
             "(boolean)": bool, None: None}


def parse_func(function):
    """
    Parse the docstring of ``function``.

    :param function: (function) function whose docstring is going to be parsed.
    :return: (dictionary of list of values) link each arguments \
    to their type and their description.
    """
    description = ""
    res_dic = {}
    doc = function.__doc__
    if doc:
        doc = filter(None, re.split("[\n\r]", doc))
        for line in doc:
            line = re.sub('\s+', ' ', line).strip()
            if ":return:" not in line and "param" not in line:
                description += line
            if ":param " in line:
                flt = list(filter(None, line.split("param")[1].split(":")))
                flt = [word.strip() for word in flt]
                if isinstance(flt[1], list):
                    flt_desc = ":".join(flt[1]).split(" ")
                else:
                    flt_desc = flt[1].split(" ")
                type_info = [type_list[w] for w in flt_desc if
                             w.replace(" ", "") in type_list.keys()]
                if len(type_info) > 1:
                    print("Warning multiple type detected for %s"
                          "only the first one will be present" % flt[0])
                if len(type_info) == 0:
                    type_info = [None]
                res_dic[flt[0]] = [type_info[0], " ".join(flt_desc)]
    else:
        description = ""
    signature = dict(inspect.signature(function).parameters)
    parsed_doc = add_dic(signature, res_dic)
    return description, parsed_doc


def init_parser(description, data_parse):
    """
    Create the parser using argparse.

    :param description: (string) the description of a function
    :param data_parse: (dictionary of list) links each arguments to it's\
    default values, it type and description.
    :return: (class ArgumentParser) the argparse parser.
    """
    parser = argparse.ArgumentParser(description=description)
    arguments = [key for key in data_parse.keys() if key != "doc"]
    rargs = parser.add_argument_group("required argument")
    for arg in arguments:
        if data_parse[arg][0] == inspect._empty:
            rargs.add_argument("--%s" % arg, dest=arg,
                               help=data_parse[arg][2],
                               required=True)
        else:
            parser.add_argument("--%s" % arg, dest=arg,
                                help=data_parse[arg][2],
                                default=data_parse[arg][0])
    return parser


def message(sentence, type_m=None):
    """
    Return a message in the correct format.

    :param sentence: (string) the message we want to return.
    :param type_m: (string or None) the type of the message to display
    :return: (string) the message in a correct format.
    """
    sentence = re.sub('\s+', ' ', sentence)
    if not type_m:
        return sentence
    if type_m == "w":
        return "\033[33m" + sentence + "\033[0m"
    else:
        return "\033[31m" + sentence + "\033[0m"


def add_dic(dic1, dic2):
    """
    Add two dictionary together.

    :param dic1: (dict of list) dictionary containing list of values.
    :param dic2: (dict of list) dictionary containing list of values.
    :return: (dictionary of list) dictionary that concatenates \
    the list in every key of dic1 and dic2.
    """
    list_k = list(dic1.keys())
    if sorted(list_k) != sorted(list(dic2.keys())):
        print(message("WARNING : the signature of the function and \
                      it's docstring have not the same param names !",
                      type_m="w"))
    new_dic = {}
    for k in list_k:
        if k in dic2.keys():
            new_dic[k] = [dic1[k].default] + dic2[k]
        else:
            new_dic[k] = [dic1[k].default] + ["(str)", "(str) param %s" % k]
    return new_dic


def wrap(function):
    """
    Wrapper of the function ``function``.

    :param function: (function) the function to wrap
    :return: (LazyParser call_func method) the method calling `` function``.
    """

    @functools.wraps(function)
    def call_func():
        """
        Call the function ``self.func`` and return it's result.

        :return: the result of the function ``self.func``
        """
        description, data_parse = parse_func(function)
        parser = init_parser(description, data_parse)
        args = parser.parse_args()
        str_args = ""
        for my_arg in data_parse.keys():
            try:
                statement = "args.{0} = data_parse[my_arg][1](args.{0})"
                exec(statement.format(my_arg))
            except ValueError:
                msg = message("argument --{0} must be a {1}",
                              type_m="e")
                type_arg = data_parse[my_arg][1].__name__
                parser.error(msg.format(my_arg, type_arg))
            str_args += "%s=args.%s, " % (my_arg, my_arg)
        str_args = str_args[:-2]
        return eval("function(%s)" % str_args)
    return call_func
