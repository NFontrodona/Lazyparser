#!/usr/bin/env python3

# -*- coding utf-8 -*-

"""
Author : Fontrodona Nicolas (2019)

Description:
    This script define the lazyparser.
"""

import argparse
from argparse import FileType
import re
import inspect
import functools
import os

__version__ = 0.1

type_list = {"(int)": int, "(float)": float, "(string)": str, "(str)": str,
             "(file)": str, "(bool)": bool,
             "(function)": object,
             "(boolean)": bool, None: None}


class Argument(object):
    """
    Represent a Lazyparser Argument.
    """
    def __init__(self, name_arg, default, arg_type):
        """
        Initiate the creation of an argument.

        :param name_arg: (string) the name of the argument
        :param default: the default value of the argument
        :param arg_type: (type) the type of the argument
        """
        self.name = name_arg
        self.type = None if arg_type == inspect._empty else \
            (arg_type if isinstance(arg_type, type) else None)
        self.default = str(default) if default in [True, False] else \
            (default if default != inspect._empty else None)
        self.help = "param %s" % self.name
        self.short_name = None
        self.choice = None
        self.value = None
        self.const = "$$void$$"

    def update_default(self, default):
        """
        Update the default value of self if it set to None.

        :param default: (value)
        """
        self.default = self.default if self.default else default

    def update_type(self, arg_type):
        """
        Update the type value of self if it set to None.

        :param arg_type: (value)
        """
        self.type = self.type if self.type else arg_type

    def gfn(self):
        """
        Get the full name of the argument.

        :return: (string) the full name of the argument
        """
        if self.short_name:
            name_arg = "-%s/--%s" % (self.short_name, self.name)
        else:
            name_arg = "--%s" % self.name
        return name_arg

    def argparse_type(self):
        """
        :return: (type)
        """
        if self.type in [bool, object]:
            return str
        else:
            return self.type

    def argparse_choice(self):
        """
        :return: (value)
        """
        if isinstance(self.choice, str):
            return None
        else:
            return self.choice


class Lazyparser(object):
    """
    Lazyparser class.
    """
    def __init__(self, function, const, choice):
        """
        Initialization with a function.

        :param function: (object) a function
        :param const: (dictionary) param that don't need to be filled.
        :param choice: (dictionary) the contains
        """
        self.func = function
        sign = dict(inspect.signature(function).parameters)
        self.args = {k: Argument(k, sign[k].default, sign[k].annotation) for
                     k in sign.keys()}
        self.help = self.description()
        self.update_param()
        self.get_short_name()
        self.set_filled(const)
        self.set_constrain(choice)

    def description(self):
        """
        Get the description of self.function.

        :return: (string) description of self.func
        """
        if not self.func.__doc__:
            return ""
        else:
            description = ""
            doc = filter(None, re.split("[\n\r]", self.func.__doc__))
            for line in doc:
                line = re.sub(r"\s+", ' ', line).strip()
                if ":return:" not in line and "param" not in line:
                    description += line
            return description

    def update_type(self, arg_name, help_info):
        """
        Update the type of an empty parameter.

        :param arg_name: (string) the name of the argument
        :param help_info: (list of string) the list string representing the \
        help for the parameter ``arg_name``
        """
        type_info = [get_type(w.replace(" ", ""), self.args[arg_name])
                     for w in help_info if re.search(r"\(.*\)", w) and
                     re.search(r"\(.*\)", w).span() == (0, len(w))]
        if len(type_info) > 1:
            msg = "multiple type detected for %s only the first was selected"
            print(message(msg % arg_name, self.args[arg_name], "w"))
        self.args[arg_name].type = type_info[0]

    def update_param(self):
        """
        Update if needed the type and the help of every args.
        """
        if self.func.__doc__:
            doc = filter(lambda x: ":param" in x,
                         re.split("[\n\r]", self.func.__doc__))
            for line in doc:
                flt = list(filter(None, line.split(":param")[1].split(":")))
                flt = [word.strip() for word in flt]
                if flt[0] in self.args.keys():
                    if isinstance(flt[1], list):
                        flt_desc = ":".join(flt[1]).split(" ")
                    else:
                        flt_desc = flt[1].split(" ")
                    self.args[flt[0]].help = " ".join(flt_desc)
                    if not self.args[flt[0]].type:
                        self.update_type(flt[0], flt_desc)

    def get_short_name(self):
        """
        Get the short param name of self.args
        """
        param_names = sorted(list(self.args.keys()))
        selected_param = []
        for param in param_names:
            sn = get_name(param, selected_param)
            self.args[param].short_name = sn
            selected_param.append(sn)

    def set_filled(self, const):
        """
        Set if a parameter can just be called without a value and \
        it values if it is called.

        :param const: (dictionary) value to set to a param called.
        """
        if const and not isinstance(const, dict):
            print("warning: const must be a dictionary")
        elif const and isinstance(const, dict):
            for marg in const.keys():
                if marg in self.args.keys():
                    mtype = self.args[marg].type
                    if not isinstance(const[marg], mtype):
                        print(message("invalid const type %s" % mtype.__name__,
                                      self.args[marg], "e"))
                        exit(1)
                    if not isinstance(self.args[marg].default, mtype):
                        print(message("invalid default type %s" % mtype.__name__,
                                      self.args[marg], "e"))
                        exit(1)

                    self.args[marg].const = const[marg]

    def set_constrain(self, choices):
        """
        Set the contains for every param in self.args.

        :param choices: (dictionary of values) the constrains
        """
        for marg in choices.keys():
            if marg in self.args.keys():
                if isinstance(choices[marg], str) and choices[marg] != "dir":
                    self.args[marg].choice = " %s " % choices[marg]
                else:
                    self.args[marg].choice = choices[marg]


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


def get_type(type_arg, argument):
    """
    Get the type of an argument.

    :param type_arg: (string) an argument type
    :param argument: (lazyparse argument) an argument type
    :return: (Type) the type of ``type_arg``
    """
    if type_arg in type_list.keys():
        return type_list[type_arg]
    elif "FileType" in type_arg:
        my_line = re.split(r"[()]", type_arg)
        if len(my_line) != 5:
            msg = "wrong definition of FileType "
            msg += "(choose from FileType, FileType('w') w:open mode "
            msg += ": set to str"
            print(message(msg, argument, "w"))
            return str
        else:
            my_line[2] = re.sub(r"[\"\']", "", my_line[2])
            return FileType(my_line[2])
    else:
        msg = "unknown type: type set to string"
        print(message(msg, argument, "w"))
        return str


def init_parser(lp):
    """
    Create the parser using argparse.

    :param lp: (Lazyparser object) the parser
    :return: (ArgumentParser object) the argparse parser.
    """
    parser = argparse.ArgumentParser(description=lp.help)
    rargs = parser.add_argument_group("required arguments")
    for arg in lp.args.keys():
        mchoice = lp.args[arg].argparse_choice()
        mtype = lp.args[arg].argparse_type()
        if lp.args[arg].const == "$$void$$" and not lp.args[arg].default:
            rargs.add_argument("-%s" % lp.args[arg].short_name, "--%s" % arg,
                               dest=arg, help=lp.args[arg].help, type=mtype,
                               choices=mchoice, required=True)
        elif lp.args[arg].const == "$$void$$" and lp.args[arg].default:
            parser.add_argument("-%s" % lp.args[arg].short_name, "--%s" % arg,
                                dest=arg, help=lp.args[arg].help, type=mtype,
                                choices=mchoice, default=lp.args[arg].default)
        elif lp.args[arg].const != "$$void$$" and not lp.args[arg].default:
            print(message("const must be specified with default", lp.args[arg],
                          "e"))
            exit(1)
        else:
            parser.add_argument("-%s" % lp.args[arg].short_name, "--%s" % arg,
                                dest=arg, help=lp.args[arg].help,
                                action="store_const", const=lp.args[arg].const,
                                default=lp.args[arg].default)
    return parser


def message(sentence, argument, type_m=None):
    """
    Return a message in the correct format.

    :param sentence: (string) the message we want to return.
    :param argument: (Argument object) a Lazyparser argument.
    :param type_m: (string or None) the type of the message to display
    :return: (string) the message in a correct format.
    """
    sentence = re.sub(r"\s+", ' ', sentence)
    sentence = "argument %s: " % argument.gfn() + sentence
    if not type_m:
        return sentence
    if type_m == "w":
        return "warning: " + sentence
    if type_m == "e":
        return "error: " + sentence


def tests_function(marg, parser):
    """
    Performs the test conditions wanted.

    :param marg: (Argument object) a lazyparser argument
    :param parser: (class ArgumentParser) the argparse parser.
    """
    spaced_n = " %s " % marg.name
    spaced_sn = " %s " % marg.short_name
    if isinstance(marg.choice, str) and marg.choice != "dir":
        if spaced_n in marg.choice or spaced_sn in marg.choice:
            if spaced_n in marg.choice:
                cond = marg.choice.replace(spaced_n, str(marg.value))
            else:
                cond = marg.choice.replace(spaced_sn, str(marg.value))
            try:
                if not eval(cond):
                    msg = "invalid choice %s: it must respect : %s"
                    parser.error(message(msg % (marg.value, marg.choice),
                                         marg))
            except (SyntaxError, TypeError, NameError):
                msg = "wrong assertion: %s. It will be ignored"
                print(message(msg % marg.choice, marg, "w"))
        else:
            msg = "not found in assertion: %s. It will be ignored"
            print(message(msg % marg.choice, marg, "w"))
    if isinstance(marg.choice, str) and marg.choice == "dir":
        eval_str = os.path.isdir(marg.value)
        relevant = isinstance(marg.value, str)
        if relevant and isinstance(marg.choice, str) and not eval_str:
            msg = "invalid choice %s: it must be an existing dir"
            parser.error(message(msg % marg.value, marg))
        if not relevant:
            msg = "not a string and therefore can't be a file."
            print(message(msg, marg, "w"))


def test_type(marg, parser):
    """
    Performs the type test conditions wanted.

    :param marg: (Argument object) a lazyparser argument
    :param parser: (class ArgumentParser) the argparse parser.
    """
    if marg.type == object:
        try:
            marg.value = eval(marg.value)
        except (SyntaxError, TypeError, NameError):
            msg = "Not a function %s" % marg.value
            parser.error(message(msg, marg))
    elif marg.type == bool:
        print("'%s'" % marg.value)
        if marg.value == "True":
            marg.value = True
        elif marg.value == "False":
            marg.value = False
        else:
            msg = "invalid bool type %s (choose from True, False)"
            parser.error(message(msg % marg.value, marg))
    return marg.value


def wrapper(func=None, const=None, **kwargs):
    """

    :param func: (function) the function of interest
    :param const: (dictionary) the params that don't need a value to fill.
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
        def call_func(mfilled=const):
            """
            Call the function ``self.func`` and return it's result.

            :return: the result of the function ``self.func``
            """
            lazyparser = Lazyparser(function, mfilled, kwargs)
            parser = init_parser(lazyparser)
            args = parser.parse_args()
            str_args = ""
            for my_arg in lazyparser.args.keys():
                lazyparser.args[my_arg].value = eval("args.%s" % my_arg)
                if lazyparser.args[my_arg].choice:
                    tests_function(lazyparser.args[my_arg], parser)
                exec("args.%s = test_type(lazyparser.args[my_arg], parser)"
                     % my_arg)
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


def flag(func=None, **kwargs):
    """
    Function used to set a value to some parameters when they are called.

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
            return function(kwargs)
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