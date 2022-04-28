#!/usr/bin/env python3

# -*- coding utf-8 -*-

"""
Author : Fontrodona Nicolas (2019)

Copyright 2019 Fontrodona Nicolas

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


This script define the lazyparser.
"""

import re
import inspect
import functools
import itertools
import sys
import os
import io
import argparse
import typing


__version__ = '0.2.1'
__all__ = ('List', 'set_env', 'set_epilog', 'set_groups', 'parse', 'flag')


#####################################
# sets the docstring environment
pd1 = ":param"  # param delimiter 1
pd2 = ":"  # param delimiter 2
header = ""  # header of arguments
tab = 4  # number of spaces composing tabulations
epi = None  # epilog for the parser
groups = {}  # the groups of arguments
lpg_name = {}  # the name of the parser used
grp_order = None  # the order of groups
optionals_title = "Optional arguments"
required_title = "Required arguments"
help_arg = True
######################################


class List(object):
    """
    Creation of a vector class
    """
    def __init__(self, size="+", vtype=None, value=None):
        """
        Initiate the vector class.

        :param size: (int or str) the size of the vector
        :param vtype: (type) the type of the vector
        :param value: (values)
        """
        if size != "+":
            try:
                self.size = int(size)
            except ValueError:
                print("Error : size must be an int or '+' symbol")
                exit(1)
        else:
            self.size = size
        if vtype is None:
            self.type = str
        else:
            self.type = vtype
        if value:
            if not isinstance(value, (list, tuple)):
                print("error : %s not a list or tuple" % value)
                exit(1)
            self.value = value
        else:
            self.value = None


def handled_type(atype, htype="m"):
    """
    Get the type of an argument.

    :param atype: (type) a type
    :param htype: (str) m for subtype and s for subtype
    :return: (type) the type of an argument
    """
    dic_type = {"m": [int, float, bool, str, List],
                "s": [int, float, bool, str]}
    if isinstance(atype, List):
        atype = type(atype)
    if atype in dic_type[htype]:
        return True
    else:
        return False


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
        self.default = default
        self.help = "param %s" % self.name
        self.short_name = None
        self.choice = None
        self.value = None
        self.const = "$$void$$"
        self.type = self.set_type(arg_type)
        self.pgroup = self.get_parser_group()

    def __eq__(self, arg):
        """
        Compare to Argument object and say if they are equal.

        :param arg: (Argument object)
        """
        return self.name == arg.name and \
            self.default == arg.default and \
            self.help == arg.help and \
            self.short_name == arg.short_name and \
            self.choice == arg.choice and \
            self.value == arg.value and \
            self.const == arg.const and \
            self.type == arg.type and \
            self.pgroup == arg.pgroup

    def get_type(self):
        """

        :return:(type) the type of self
        """
        if isinstance(self.type, type):
            return self.type
        else:
            return type(self.type)

    def set_type(self, arg_type):
        """
        Set the type of self argument.

        :param arg_type: (type or class instance) a type
        :return: (type) the type of the argument
        """
        arg_type = handle_list_typing_type(arg_type)
        if arg_type == inspect._empty:
            return inspect._empty
        if handled_type(arg_type):
            check_subtype(arg_type, self)
            return arg_type
        if isinstance(arg_type, type):
            msg = "Not handled type %s" % arg_type.__name__
        else:
            msg = "unknown type %s" % str(arg_type)
        print(message(msg, self, "e"))
        exit(1)

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
        if self.type == bool:
            return str
        elif isinstance(self.type, List):
            if self.type.type == bool:
                return str
            else:
                return self.type.type
        else:
            return self.type

    def argparse_narg(self):
        if not isinstance(self.type, List):
            return None
        else:
            return self.type.size

    def argparse_metavar(self):
        """
        :return: (string) the metavar for the argument
        """
        if isinstance(self.type, List):
            if self.type.size == "+":
                return "List[%s]" % self.type.type.__name__
            else:
                return "List[%s,%s]" % (self.type.size,
                                        self.type.type.__name__)
        else:
            return self.type.__name__.replace("Function", "Func")

    def argparse_choice(self):
        """
        :return: (value)
        """
        if isinstance(self.choice, str):
            return None
        elif isinstance(self.choice, bool):
            return str(self.choice)
        elif isinstance(self.choice, (list, tuple)):
            choice = []
            for v in self.choice:
                if isinstance(v, bool):
                    choice.append(str(v))
                elif callable(v):
                    name = os.path.basename(sys.argv[0])
                    print("%s: error: parse: functions to respect must be "
                          "given in str format" % name)
                    exit(1)
                else:
                    choice.append(v)
            return choice
        elif callable(self.choice):
            name = os.path.basename(sys.argv[0])
            print("%s: error: parse: function to respect must be given "
                  "in str format" % name)
            exit(1)
        else:
            return self.choice

    def get_parser_group(self):
        """
        Get the group name of the wanted argument.

        :return: (list of 2 string or NoneType) The name of the parser \
        followed by the names of the group of arguments
        """
        for key in groups.keys():
            if self.name in groups[key]:
                if "help" in groups[key]:
                    return ["__parser__", key]
                else:
                    return [lpg_name[key], key]
        if self.default == inspect._empty:
            return ["__rarg__", required_title]
        else:
            return ["__parser__", optionals_title]


class Lazyparser(object):
    """
    Lazyparser class.
    """
    def __init__(self, function, const, choice):
        """
        Initialization with a function.

        :param function: (function) a function
        :param const: (dictionary) param that don't need to be filled.
        :param choice: (dictionary) the contains
        """
        self.func = function
        self.args, self.order = self.init_args()
        self.help = self.description()
        self.update_param()
        self.get_short_name()
        self.set_filled(const)
        self.set_constrain(choice)

    def __eq__(self, parser):
        """
        Compare to parser and say if they are the same. \
        Note that the functions defining the two Lazyparser object \
        can be different but if those function have the same signature \
        this function will return True as they will store the same arguments.

        :param parser: (Lazyparser object)
        :return: (bool)
        """
        return self.args == parser.args and \
            self.order == parser.order and \
            self.help == parser.help

    def init_args(self):
        """
        Initiate the creation the argument of interest.
        """
        sign = inspect.signature(self.func).parameters
        if "help" not in sign.keys():
            dic_args = {k: Argument(k, sign[k].default, sign[k].annotation)
                        for k in sign.keys()}
            if help_arg:
                dic_args["help"] = Argument("help", "help", str)
                return dic_args, ["help"] + list(sign.keys())
            return dic_args, list(sign.keys())
        else:
            print("error: argument conflict, help argument cannot be set in"
                  "the parsed function")
            exit(1)

    def description(self):
        """
        Get the description of self.function.

        :return: (string) description of self.func
        """
        if not self.func.__doc__:
            return ""
        else:
            description = ""
            doc = iter(re.split("[\n\r]", self.func.__doc__))
            doc = itertools.dropwhile(lambda x: x == "", doc)
            if pd1 == "":
                delim = pd2
            else:
                delim = pd1
            if not header:
                doc = itertools.takewhile(lambda x: delim not in x, doc)
            else:
                doc = itertools.takewhile(lambda x: delim not in x
                                          and header not in x, doc)
            for line in doc:
                if line[0:tab].strip() == "":
                    line = line[tab:]
                else:
                    line = line.lstrip()
                if description:
                    description += "\n" + line
                else:
                    description = line
            return description

    def update_type(self, arg_name, help_info):
        """
        Update the type of an empty parameter.

        :param arg_name: (string) the name of the argument
        :param help_info: (list of string) the list string representing the \
        help for the parameter ``arg_name``
        """
        type_info = [get_type(w, self.args[arg_name])
                     for w in help_info if re.search(r"\(.+\)", w) and
                     re.search(r"\(.+\)", w).span() == (0, len(w))]
        if len(type_info) > 1:
            msg = "multiple type detected for %s only the first was selected"
            print(message(msg % arg_name, self.args[arg_name], "w"))

        if type_info:
            self.args[arg_name].type = type_info[0][0]
            self.args[arg_name].help = \
                self.args[arg_name].help.replace(type_info[0][1], "").strip()

    def update_param(self):
        """
        Update if needed the type and the help of every args.
        """
        if self.func.__doc__:
            doc = filter(lambda x: pd1 in x and pd2 in x,
                         re.split("[\n\r]", self.func.__doc__))
            for line in doc:
                if pd1 != "":
                    flt = list(filter(None, line.split(pd1)[1].split(pd2)))
                else:
                    flt = list(filter(None, line.split(pd2)))
                flt = [word for word in flt]
                flt[0] = flt[0].strip()
                if flt[0] in self.args.keys():
                    if len(flt[1:]) > 1:
                        flt_desc = pd2.join(flt[1:])
                    else:
                        flt_desc = flt[1]
                    self.args[flt[0]].help = flt_desc
                    if self.args[flt[0]].type == inspect._empty:
                        self.update_type(flt[0], handle(flt_desc))

    def get_short_name(self):
        """
        Get the short param name of self.args
        """
        param_names = sorted(list(self.args.keys()))
        if "help" in param_names:
            self.args["help"].short_name = "h"
            selected_param = ["h"]
            del(param_names[param_names.index("help")])
        else:
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
        msg = "invalid flag type %s"
        if const and not isinstance(const, dict):
            print("warning: flags must be defined as a dictionary")
        elif const and isinstance(const, dict):
            for marg in const.keys():
                if marg in self.args.keys():
                    mtype = self.args[marg].get_type()
                    if mtype == List:
                        if not isinstance(const[marg], (list, tuple)):
                            print(message(msg % mtype.__name__,
                                          self.args[marg], "e"))
                            exit(1)
                    elif not handled_type(mtype, "m"):
                        print(message(msg % mtype.__name__,
                                      self.args[marg], "e"))
                        exit(1)
                    elif mtype == float:
                        if not isinstance(const[marg], (int, float)):
                            print(message(msg % mtype.__name__,
                                  self.args[marg], "e"))
                            exit(1)
                    elif not isinstance(const[marg], mtype):
                        print(message(msg % mtype.__name__,
                                      self.args[marg], "e"))
                        exit(1)
                    if not isinstance(self.args[marg].default, mtype):
                        if mtype == List:
                            if not isinstance(self.args[marg].default,
                                              (list, tuple)):
                                print(message(msg % mtype.__name__,
                                              self.args[marg], "e"))
                                exit(1)
                        elif mtype == float:
                            if not isinstance(self.args[marg].default,
                                              (float, int)):
                                print(message(msg % mtype.__name__,
                                              self.args[marg], "e"))
                                exit(1)
                        elif self.args[marg].default == inspect._empty:
                            msg = "default value required"
                            print(message(msg,
                                          self.args[marg], "e"))
                            exit(1)
                        else:
                            msg = msg.replace("const", "default")
                            print(message(msg %
                                          mtype.__name__,
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
                if isinstance(choices[marg], str) and \
                        choices[marg] not in ["dir", "file"]:
                    self.args[marg].choice = " %s " % choices[marg]
                else:
                    self.args[marg].choice = choices[marg]

    def get_order(self):
        """
        Get the order of groups of argument to display.

        :return: (list of str) the ordered list of arguments to display.
        """
        if grp_order is None:
            return self.order
        else:
            dic_args = {}
            list_args = []
            for narg in self.order:
                arg = self.args[narg]
                if arg.pgroup[1] not in dic_args.keys():
                    dic_args[arg.pgroup[1]] = [narg]
                else:
                    dic_args[arg.pgroup[1]].append(narg)
            for grp_arg in grp_order:
                if grp_arg not in dic_args.keys():
                    print("Error the argument group %s don't exists" % grp_arg)
                    exit(1)
                else:
                    list_args += dic_args.pop(grp_arg)
            for key in dic_args:
                list_args += sorted(dic_args[key])
            return list_args


def set_env(delim1=":param", delim2=":", hd="", tb=4):
    """
    Change the param delimiters.

    :param delim1: (string) param delimiter 1
    :param delim2: (string) param delimiter 2
    :param hd: (string) the header of parameter
    :param tb: (int) the number of space/tab that bedore the docstring
    """
    if isinstance(tb, int):
        global tab
        tab = tb
    else:
        tab = 4
    args = [delim1, delim2, hd]
    if sum([not isinstance(a, str) for a in args]) > 0:
        print("error : delim1 and delim2 must be strings")
        exit(1)
    for i in range(len(args)):
        args[i] = args[i].replace("\n", "")
        args[i] = args[i].replace("\r", "")
        args[i] = args[i].replace("\t", "")
        args[i] = args[i].replace(" ", "")
    if not delim2:
        print("error : bad delim2 definition")
        exit(1)
    else:
        global pd1
        pd1 = delim1
        global pd2
        pd2 = delim2
        global header
        header = hd


def set_epilog(epilog):
    """
    Allow the user to define an epilog for the parser.

    :param epilog: (str) a parser epilog.
    """
    if isinstance(epilog, str):
        global epi
        epi = epilog


def set_groups(arg_groups=None, order=None, add_help=True):
    """
    Change the name of the argument groups.

    :param order: (list of string) the order of groups the user wants
    :param arg_groups: (dictionary of list of string) links each arguments to \
    its groups.
    :param add_help: (bool) True to display the help, false else.
    """
    pname = {}
    tmp = []
    help_name = "Optional arguments"
    if arg_groups:
        for key in arg_groups.keys():
            if "help" in arg_groups[key]:
                help_name = key
                n = "__parser__"
            else:
                n = "".join(re.findall(r"[A-Za-z0-9_]", key))
                n = re.sub(r"^[0-9]*", "", n)
                if len(n) == 0:
                    print("Error : The name '%s' must have at least one of the"
                          "following symbols [A-Za-z]" % key)
                    exit(1)
            pname[key] = n
            if n not in tmp:
                tmp.append(n)
            else:
                print("Error %s after removing symbols not in [A-Za-z0-9]"
                      "is already defined" % key)
                exit(1)
    global groups
    groups = arg_groups if arg_groups is not None else {}
    global lpg_name
    global grp_order
    grp_order = order
    lpg_name = pname
    if isinstance(add_help, bool):
        global help_arg
        help_arg = add_help
    global optionals_title
    optionals_title = help_name


def handle(seq):
    """
    Return only string surrounded by ().

    :param seq: (string) the string to process
    :return: (list of string) list of word in seq sourrounded by ()
    """
    seq = seq.replace("()", "")
    start = 0
    res = []
    word = ""
    for w in seq:
        if w == "(":
            start += 1
            if start == 1:
                word = "("
            else:
                word += "("
        elif w == ")":
            start -= 1
            word += ")"
            if start == 0:
                res.append(word)
        elif start > 0:
            word += w
    return res


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
    ft = type_arg
    type_arg = type_arg.replace(" ", "")
    try:
        type_arg = type_arg.replace("(List)", "(List())")
        if "[" in type_arg and "," not in type_arg:
            type_arg = type_arg.replace("[", "(vtype=").replace("]", ")")
        if type_arg != "(string)":
            type_arg = eval(type_arg)
        else:
            type_arg = str
    except (SyntaxError, TypeError, NameError):
        msg = "unknown type %s" % type_arg
        print(message(msg, argument, "e"))
        exit(1)
    if handled_type(type_arg):
        check_subtype(type_arg, argument)
        return type_arg, ft


def handle_list_typing_type(arg_type):
    """
    Turn a list from the typing module into a lazyparser list.

    :param arg_type: (type or class instance) a type
    :return:
    """
    if isinstance(arg_type, type(typing.List[typing.Any])):
        try:
            if arg_type.__name__ == 'List':  # for python 3.5
                arg_type = List(vtype=arg_type.__args__[0])
        except AttributeError:
            if arg_type._name == "List":  # for python 3.7
                arg_type = List(vtype=arg_type.__args__[0])
        return arg_type
    return arg_type


def check_subtype(argtype, arg):
    """
    check if the subtype is supported.

    :param argtype: (type or List instance) a type or list object
    :param arg: (Argument object) an Argument
    """
    if isinstance(argtype, List):
        if not handled_type(argtype.type, "s"):
            print(message("unknown %s subtype of %s" %
                          (argtype, argtype.type), arg, "e"))
            exit(1)


class NewFormatter(argparse.RawDescriptionHelpFormatter):
    """
        New argparse Help Formatter
    """

    def __init__(self, prog):
        """
        Initiate the creation of the NewFormatter object.

        :param prog: (str) the program filename.
        """
        # increase the max_help_position from 24 to 50.
        super().__init__(prog, max_help_position=50, width=120)

    def _format_args(self, action, default_metavar):
        get_metavar = self._metavar_formatter(action, default_metavar)
        result = '%s' % get_metavar(1)
        return result

    def _format_action_invocation(self, action):
        """
        :param action: (argparse._StoreAction object) convert command line \
        strings to python object.
        :return: (str) parameter invocation string
        """
        parts = []
        if action.nargs == 0:
            parts.extend(action.option_strings)
        else:
            dft = self._get_default_metavar_for_optional(action)
            args_string = self._format_args(action, dft)
            for option_string in action.option_strings:
                parts.append(option_string)
            return '%s %s' % (', '.join(parts), args_string)
        return ', '.join(parts)

    def _get_default_metavar_for_optional(self, action):
        """

        :param action: (argparse._StoreAction object) convert command line \
        strings to python object.
        :return: (str) the default metavar names
        """
        return action.dest[0].upper()


def init_parser(lp):
    """
    Create the parser using argparse.

    :param lp: (Lazyparser object) the parser
    :return: (ArgumentParser object) the argparse parser.
    """
    parser = argparse.ArgumentParser(formatter_class=NewFormatter,
                                     description=lp.help,
                                     add_help=False,
                                     epilog=epi)
    pgroups = []
    for arg in lp.get_order():
        if lp.args[arg].type == inspect._empty:
            lp.args[arg].type = str
        pgroup = lp.args[arg].pgroup[0]
        pname = lp.args[arg].pgroup[1]
        if pgroup not in pgroups:
            exec("%s = parser.add_argument_group('%s')" % (pgroup, pname))
            pgroups.append(pgroup)
        mchoice = lp.args[arg].argparse_choice()  # noqa
        mtype = lp.args[arg].argparse_type()  # noqa
        nargs = lp.args[arg].argparse_narg()  # noqa
        metvar = lp.args[arg].argparse_metavar().upper()  # noqa
        if arg == "help":
            cmd = """{}.add_argument("-%s" % lp.args[arg].short_name,
                                     "--%s" % arg,
                                     action="help",
                                     help="show this help message and exit")
                                     """.format(pgroup)
            exec(cmd)
            del(lp.args[arg])
        elif lp.args[arg].const == "$$void$$" and \
                lp.args[arg].default == inspect._empty:
            cmd = """{}.add_argument('-%s' % lp.args[arg].short_name,
                                        '--%s' % arg, dest=arg,
                                        help=lp.args[arg].help, type=mtype,
                                        metavar=metvar,
                                        choices=mchoice, nargs=nargs,
                                        required=True)""".format(pgroup)
            exec(cmd)
        elif lp.args[arg].const == "$$void$$" and lp.args[arg].default != \
                inspect._empty:
            cmd = """{}.add_argument("-%s" % lp.args[arg].short_name,
                                     "--%s" % arg,
                                     dest=arg, help=lp.args[arg].help,
                                     type=mtype, metavar=metvar,
                                     choices=mchoice, nargs=nargs,
                                     default=lp.args[arg].default)
                                     """.format(pgroup)
            exec(cmd)
        else:
            cmd = """{}.add_argument("-%s" % lp.args[arg].short_name,
                                     "--%s" % arg, dest=arg,
                                     help=lp.args[arg].help,
                                     action="store_const", metavar="",
                                     const=lp.args[arg].const,
                                     default=lp.args[arg].default)
                                     """.format(pgroup)
            exec(cmd)
    return parser


def message(sentence, argument, type_m=None):
    """
    Return a message in the correct format.

    :param sentence: (string) the message we want to return.
    :param argument: (Argument object) a Lazyparser argument.
    :param type_m: (string or None) the type of the message to display
    :return: (string) the message in a correct format.
    """
    name = os.path.basename(sys.argv[0])
    sentence = re.sub(r"\s+", ' ', sentence)
    sentence = "argument %s: " % argument.gfn() + sentence
    if not type_m:
        return sentence
    if type_m == "w":
        return name + ": warning: " + sentence
    if type_m == "e":
        return name + ": error: " + sentence


def tests_function(marg, parser):
    """
    Performs the test conditions wanted.

    :param marg: (Argument object) a lazyparser argument
    :param parser: (class ArgumentParser) the argparse parser.
    """
    spaced_n = " %s " % marg.name
    spaced_sn = " %s " % marg.short_name
    if isinstance(marg.choice, str) and marg.choice not in ["dir", "file"]:
        if not isinstance(marg.type, List):
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
        else:
            if spaced_n in marg.choice or spaced_sn in marg.choice:
                if spaced_n in marg.choice:
                    cond = marg.choice.replace(spaced_n, "$$!$$")
                else:
                    cond = marg.choice.replace(spaced_sn,  "$$!$$")
                for val in marg.value:
                    mcond = cond.replace("$$!$$", str(val))
                    try:
                        if not eval(mcond):
                            msg = "invalid choice %s: it must respect : %s"
                            parser.error(message(msg % (val, marg.choice),
                                                 marg))
                    except (SyntaxError, TypeError, NameError):
                        msg = "wrong assertion: %s. It will be ignored"
                        print(message(msg % marg.choice, marg, "w"))
            else:
                msg = "not found in assertion: %s. It will be ignored"
                print(message(msg % marg.choice, marg, "w"))

    if isinstance(marg.choice, str) and marg.choice in ["dir", "file"]:
        relevant = isinstance(marg.value, (str, io.IOBase))
        if not relevant and not isinstance(marg.type, List):
            msg = "Wrong file type."
            parser.error(message(msg, marg))
        else:
            if isinstance(marg.value, str):
                eval_str = eval("os.path.is%s(marg.value)" % marg.choice)
                if relevant and not eval_str:
                    msg = "invalid choice %s: it must be an existing %s"
                    parser.error(message(msg % (marg.value, marg.choice),
                                         marg))
            elif isinstance(marg.value, list):
                for mfile in marg.value:
                    eval_str = eval("os.path.is%s(mfile)" % marg.choice)
                    if not eval_str:
                        msg = "invalid choice %s: it must be an existing %s"
                        parser.error(message(msg % (mfile, marg.choice),
                                             marg))


def test_type(marg, parser):
    """
    Performs the type test conditions wanted.

    :param marg: (Argument object) a lazyparser argument
    :param parser: (class ArgumentParser) the argparse parser.
    """
    dic = {"True": True, "False": False, True: True, False: False}
    if marg.type == bool:
        try:
            marg.value = dic[marg.value]
        except KeyError:
            msg = "invalid bool type %s (choose from True, False)"
            parser.error(message(msg % marg.value, marg))
    elif isinstance(marg.type, List):
        if marg.type.type == bool:
            try:
                marg.value = [dic[v] for v in marg.value]
            except KeyError:
                msg = "invalid bool type in %s (choose from True, False)"
                parser.error(message(msg % marg.value, marg))
    return marg.value


def parse(func=None, const=None, **kwargs):
    """
    Create the parser.

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
            args = parser.parse_args()  # noqa
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

    :param func: (function) the function to wrap
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
