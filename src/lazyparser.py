#!/usr/bin/env python3

# -*- coding utf-8 -*-

"""
Author : Fontrodona Nicolas (2019)

Description:
    This script define the lazyparser.
"""

import argparse
import re
import inspect
import functools
import os


__version__ = 0.1


def give_arg_vals(arg_value):
    """
    Give a string message giving the value of  ``arg_value``.

    :param arg_value: (value) the value of an argument
    :return: (string) string indicating the value of ``arg_value``
    """
    if isinstance(arg_value, str):
        val = "(of value '%s')" % arg_value
    else:
        val = "(of value %s)" % arg_value
    return val


def none_func(value, argname):
    """
    Say if a value can be a NoneType value.

    :param value: (value) a variable
    :param argname: (string) the name of the argument
    :return: (value) the value or NoneType if value = "None"
    """
    if value == "None":
        return None
    val = give_arg_vals(value)
    msg = "WARNING the argument --%s %s is not None" \
          " it's type will be set to str" % (argname, val)
    print(message(msg, "w"))
    return value


type_list = {"(int)": int, "(float)": float, "(string)": str, "(str)": str,
             "(file)": str, "(bool)": bool,
             "(boolean)": bool, None: None,
             "(None)": none_func,
             "(NoneType)": none_func}


def get_name(name, list_of_name, size=1):
    """

    :param name: (string) the param name
    :param list_of_name: (string) the list of param name
    :param size: (int) the size of the name used
    :return: (string) the param name selected
    """
    if name[0:size] not in list_of_name:
        return name[0:size]
    elif name[0:size].upper() not in list_of_name:
        return name[0:size].upper()
    else:
        return get_name(name, list_of_name, size=size + 1)


def get_short_param_name(param_names):
    """
    Get the short param name of the parameters ``param_names`` of a function.

    :param param_names: (list of string) list of param name
    :return: (dictionary of string) dictionary that links each param to \
    its short name
    """
    param_names = sorted(param_names)
    short_dic = {}
    selected_param = []
    for param in param_names:
        sn = get_name(param, selected_param)
        short_dic[param] = sn
        selected_param.append(sn)
    return short_dic


def parse_func(function, dic_test):
    """
    Parse the docstring of ``function``.

    :param function: (function) function whose docstring is going to be parsed.
    :param dic_test: (dictionary of values) the test to perform for each param.
    :return: (dictionary of list of values) link each arguments \
    to their type and their description.
    """
    description = ""
    res_dic = {}
    doc = function.__doc__
    if doc:
        doc = filter(None, re.split("[\n\r]", doc))
        for line in doc:
            line = re.sub(r"\s+", ' ', line).strip()
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
                    msg = "Warning multiple type detected for {} " \
                          "only the first one will be present"
                    print(message(msg.format(flt[0]), "w"))
                if len(type_info) == 0:
                    type_info = [None]
                res_dic[flt[0]] = [type_info[0], " ".join(flt_desc)]
    else:
        description = ""
    signature = dict(inspect.signature(function).parameters)
    short_name = get_short_param_name(list(signature.keys()))
    parsed_doc = add_dic(signature, res_dic, dic_test)
    parsed_doc = {k: parsed_doc[k] + [short_name[k]] for k in parsed_doc}
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
            rargs.add_argument("-%s" % data_parse[arg][4], "--%s" % arg,
                               dest=arg, help=data_parse[arg][2],
                               required=True)
        else:
            parser.add_argument("-%s" % data_parse[arg][4], "--%s" % arg,
                                dest=arg, help=data_parse[arg][2],
                                default=data_parse[arg][0])
    return parser


def message(sentence, type_m=None):
    """
    Return a message in the correct format.

    :param sentence: (string) the message we want to return.
    :param type_m: (string or None) the type of the message to display
    :return: (string) the message in a correct format.
    """
    sentence = re.sub(r"\s+", ' ', sentence)
    if not type_m:
        return sentence
    if type_m == "w":
        return "\033[33m" + sentence + "\033[0m"
    else:
        return "\033[31m" + sentence + "\033[0m"


def add_dic(dic1, dic2, dic_test):
    """
    Add two dictionary together.

    :param dic1: (dict of list) dictionary containing list of values.
    :param dic2: (dict of list) dictionary containing list of values.
    :param dic_test: (dict of keys) dictionary containing test values.
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
            new_dic[k] = [dic1[k].default] + [str, "(str) param %s" % k]
        if k in dic_test.keys():
            new_dic[k] += [dic_test[k]]
        else:
            new_dic[k] += ["void"]
    return new_dic


def tests_function(arg_value, arg_name, test_cond, parser):
    """
    Performs the test conditions wanted.

    :param arg_value: (value)
    :param arg_name: (string) the name of the argument
    :param test_cond: (value) test
    :param parser: (class ArgumentParser) the argparse parser.
    """
    val = give_arg_vals(arg_value)
    if isinstance(test_cond, list) and arg_value not in test_cond:
        msg = "The argument --%s %s must take it's value in %s"
        parser.error(message(msg % (arg_name, val, str(test_cond)), "e"))
    elif isinstance(test_cond, str) and test_cond in ["file", "dir"]:
        eval_str = "os.path.is%s(arg_value)" % test_cond
        relevant = isinstance(arg_value, str)
        if relevant and isinstance(test_cond, str) and not eval(eval_str):
            msg = "The argument --%s %s must be an existing %s"
            parser.error(message(msg % (arg_name, val, test_cond), "e"))
        if not relevant:
            msg = "WARNING : The argument --%s %s is not a string and " \
                  "therefore can't be a file."
            print(message(msg % (arg_name, val), "w"))
    elif isinstance(test_cond, str) and test_cond != "void":
        cond = test_cond.replace(arg_name, str(arg_value))
        try:
            if not eval(cond):
                msg = "The argument --%s %s must respect this assertion : %s"
                parser.error(message(msg % (arg_name, val, test_cond), "e"))
        except (SyntaxError, TypeError, NameError):
            msg = "WARNING : Wrong assertion for --%s argument. " \
                  "It will be ignored"
            print(message(msg % arg_name, "w"))


def wrapper(func=None, **kwargs):
    """

    :param func: (function) the function of interest
    :param kwargs: (dictionary) the named arguments
    :return: (function) wrap
    """
    def wrap(function):
        """
        Wrapper of the function ``function``.

        :param function: (function) the function to wrap
        :return: (function) the method calling `` function``.
        """
        @functools.wraps(function)
        def call_func():
            """
            Call the function ``self.func`` and return it's result.

            :return: the result of the function ``self.func``
            """
            description, data_parse = parse_func(function, kwargs)
            parser = init_parser(description, data_parse)
            args = parser.parse_args()
            str_args = ""
            for my_arg in data_parse.keys():
                try:
                    statement = "args.{0} = data_parse[my_arg][1]"
                    if data_parse[my_arg][1].__name__ == "none_func":
                        statement += "(args.{0}, '{0}')"
                    else:
                        statement += "(args.{0})"
                    exec(statement.format(my_arg))
                    tests_function(eval("args.%s" % my_arg), my_arg,
                                   data_parse[my_arg][3], parser)
                except ValueError:
                    val = give_arg_vals(eval("args.{0}".format(my_arg)))
                    msg = message("argument --{0} {1} must be a {2}",
                                  type_m="e")
                    type_arg = data_parse[my_arg][1].__name__
                    parser.error(msg.format(my_arg, val, type_arg))
                str_args += "%s=args.%s, " % (my_arg, my_arg)
            str_args = str_args[:-2]
            return eval("function(%s)" % str_args)
        return call_func
    if func is None:
        def decore_call(function):
            """
            Decorate wrap function.

            :param function: (function) the function to wrap
            :return: (function) call_func
            """
            return wrap(function)
        return decore_call
    return wrap(func)
