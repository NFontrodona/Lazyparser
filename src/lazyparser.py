#!/usr/bin/env python3

# -*- coding utf-8 -*-

"""
Author : Fontrodona Nicolas (2019)

Description:
    This script define the lazyparser.
"""

import re
import inspect
import functools
import itertools
import os  # noqa
import io
import argparse
from argparse import FileType

__version__ = 0.1

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
######################################


class Function(object):
    """
    Class representing lazyparser function.

    Made to handle both building and user defined function
    """
    pass


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
    dic_type = {"m": [int, float, Function, bool, str, FileType, List],
                "s": [int, float, Function, bool, str, FileType]}

    if not isinstance(atype, type):
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

        :param arg_type: (type) a type
        :return: (type) the type of the argument
        """
        if arg_type == inspect._empty:
            return None
        if handled_type(arg_type):
            return arg_type
        if arg_type in handled_type:
            return arg_type
        if isinstance(arg_type, type):
            msg = "unknown type %s" % arg_type.__name__
        else:
            msg = "unknown type %s" % str(arg_type)
        print(message(msg, self, "e"))
        exit(1)

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
        if self.type in [bool, Function]:
            return str
        elif isinstance(self.type, List):
            if self.type.type in [bool, Function]:
                return str
            else:
                return self.type.type
        else:
            return self.type

    def argparse_narg(self):
        if not isinstance(self.type, List):
            return "?"
        else:
            return self.type.size

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
                    print("error : parse : functions to respect must be "
                          "given in str format")
                    exit(1)
                else:
                    choice.append(v)
            return choice
        elif callable(self.choice):
            print("error : parse : function to respect must be given "
                  "in str format")
            exit(1)
        else:
            return self.choice

    def get_parser_group(self):
        """
        Get the group name of the wanted argument.

        :return: (list of 2 string or NoneType) The name of the parser \
        followed by the names of the group of arguments
        """
        if len(groups.keys()) == 0:
            if self.default == inspect._empty:
                return ["__rarg__", required_title]
            else:
                return ["__parser__", optionals_title]
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
        type_info = [get_type(w.replace(" ", ""), self.args[arg_name])
                     for w in help_info if re.search(r"\(.*\)", w) and
                     re.search(r"\(.*\)", w).span() == (0, len(w))]
        if len(type_info) > 1:
            msg = "multiple type detected for %s only the first was selected"
            print(message(msg % arg_name, self.args[arg_name], "w"))

        if type_info:
            self.args[arg_name].type = type_info[0][0]
            self.args[arg_name].help = \
                self.args[arg_name].help.replace(type_info[0][1], "")

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
                flt = [word.strip() for word in flt]
                if flt[0] in self.args.keys():
                    if isinstance(flt[1], list):
                        flt_desc = pd2.join(flt[1])
                    else:
                        flt_desc = flt[1]
                    self.args[flt[0]].help = flt_desc
                    if not self.args[flt[0]].type:
                        self.update_type(flt[0], handle(flt_desc))

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
        msg = "invalid const type %s"
        if const and not isinstance(const, dict):
            print("warning: const must be a dictionary")
        elif const and isinstance(const, dict):
            for marg in const.keys():
                if marg in self.args.keys():
                    mtype = self.args[marg].get_type()
                    if mtype == Function:
                        if isinstance(const[marg], str):
                            try:
                                const[marg] = eval(const[marg])
                            except (SyntaxError, TypeError, NameError):
                                print(message(msg % mtype.__name__,
                                      self.args[marg], "e"))
                                exit(1)
                        elif callable(const[marg]):
                            const[marg] = const[marg]
                    elif not handled_type(mtype, "s"):
                        print(message(msg % mtype.__name__,
                                      self.args[marg], "e"))
                        exit(1)
                    elif not isinstance(const[marg], mtype):
                        print(message(msg % mtype.__name__,
                                      self.args[marg], "e"))
                        exit(1)
                    elif not isinstance(self.args[marg].default, mtype):
                        if self.args[marg].default is None:
                            msg = "const must be specified with default"
                            print(message(msg,
                                          self.args[marg], "e"))
                        else:
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
            return sorted(self.args.keys())
        else:
            dic_args = {}
            list_args = []
            for narg in self.args.keys():
                arg = self.args[narg]
                if arg.pgroup[1] not in dic_args.keys():
                    dic_args[arg.pgroup[1]] = [narg]
                else:
                    dic_args[arg.pgroup[1]].append(narg)
            for grp_arg in grp_order:
                list_args += sorted(dic_args.pop(grp_arg))
            for key in dic_args:
                list_args += sorted(dic_args.pop(key))
            return list_args


def set_env(delim1, delim2, hd, tb):
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


def set_data(epilog):
    """
    Allow the user to define an epilog for the parser.

    :param epilog: (str) a parser epilog.
    """
    if isinstance(epilog, str):
        global epi
        epi = epilog


def set_groups(arg_groups, order=None):
    """
    Change the name of the argument groups.

    :param order: (list of string) the order of groups the user wants
    :param arg_groups: (dictionary of list of string) links each arguments to \
    its groups.
    """
    pname = {}
    tmp = []
    help_name = None
    if order is not None:
        for val in order:
            if val not in arg_groups:
                print("Error, the order contains groups that don't exist")
                exit(1)

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
    groups = arg_groups
    global lpg_name
    global grp_order
    grp_order = order
    lpg_name = pname
    if help_name:
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
    try:
        type_arg = type_arg.replace("(List)", "(List())")
        if type_arg != "(string)":
            type_arg = eval(type_arg)
        else:
            type_arg = str
    except (SyntaxError, TypeError, NameError):
        msg = "unknown type %s" % type_arg
        print(message(msg, argument, "e"))
        exit(1)
    if handled_type(type_arg):
        if isinstance(type_arg, List):
            if handled_type(type_arg.type, "s"):
                return type_arg, ft
            else:
                msg = "unknown %s subtype of List"
                print(message(msg % type_arg.type, argument, "e"))
                exit(1)
        return type_arg, ft


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

    def _format_action_invocation(self, action):
        """
        :param action: (argparse._StoreAction object) convert command line \
        strings to python object.
        :return: (str) parameter invocation string
        """
        if not action.option_strings:
            dft = self._get_default_metavar_for_positional(action)
            mvar, = self._metavar_formatter(action, dft)(1)
            return mvar
        else:
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
    __parser__ = argparse.ArgumentParser(formatter_class=NewFormatter,
                                         description=lp.help,
                                         epilog=epi)
    __parser__._optionals.title = optionals_title
    pgroups = []
    for arg in lp.get_order():
        pgroup = lp.args[arg].pgroup[0]
        pname = lp.args[arg].pgroup[1]
        if pgroup not in pgroups:
            exec("%s = __parser__.add_argument_group('%s')" % (pgroup, pname))
            pgroups.append(pgroup)
        lp.args[arg].pgroup[0] = __parser__.add_argument_group
        mchoice = lp.args[arg].argparse_choice()  # noqa
        mtype = lp.args[arg].argparse_type()  # noqa
        nargs = lp.args[arg].argparse_narg()  # noqa
        if lp.args[arg].const == "$$void$$" and \
                lp.args[arg].default == inspect._empty:
            cmd = """{}.add_argument('-%s' % lp.args[arg].short_name,
                                        '--%s' % arg, dest=arg,
                                        help=lp.args[arg].help, type=mtype,
                                        choices=mchoice, nargs=nargs,
                                        required=True)""".format(pgroup)
            exec(cmd)
        elif lp.args[arg].const == "$$void$$" and lp.args[arg].default:
            cmd = """{}.add_argument("-%s" % lp.args[arg].short_name,
                                     "--%s" % arg,
                                     dest=arg, help=lp.args[arg].help,
                                     type=mtype,
                                     choices=mchoice, nargs=nargs,
                                     default=lp.args[arg].default)
                                     """.format(pgroup)
            exec(cmd)
        elif lp.args[arg].const != "$$void$$" and lp.args[arg].default is None:
            print(message("const must be specified with default", lp.args[arg],
                          "e"))
            exit(1)
        else:
            cmd = """{}.add_argument("-%s" % lp.args[arg].short_name,
                                     "--" % arg, dest=arg,
                                     help=lp.args[arg].help,
                                     action="store_const",
                                     const=lp.args[arg].const,
                                     default=lp.args[arg].default)
                                     """.format(pgroup)
            exec(cmd)
    return __parser__


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
    if marg.type == Function:
        if isinstance(marg.value, str):
            try:
                marg.value = eval(marg.value)
            except (SyntaxError, TypeError, NameError):
                msg = "not a function %s" % marg.value
                parser.error(message(msg, marg))
        elif not callable(marg.value):
            msg = "not a function %s" % marg.value
            parser.error(message(msg, marg))
    elif marg.type == bool:
        try:
            marg.value = dic[marg.value]
        except KeyError:
            msg = "invalid bool type %s (choose from True, False)"
            parser.error(message(msg % marg.value, marg))
    elif isinstance(marg.type, List):
        if marg.type.type == Function:
            try:
                res = []
                for v in marg.value:
                    if isinstance(v, str):
                        res.append(eval(v))
                    elif callable(v):
                        res.append(v)
                    else:
                        msg = "not every element in %s is a function"
                        parser.error(message(msg % marg.value, marg))
                marg.value = res
            except (SyntaxError, TypeError, NameError):
                msg = "not every element in %s is a function" % str(marg.value)
                parser.error(message(msg, marg))
        elif marg.type.type == bool:

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
