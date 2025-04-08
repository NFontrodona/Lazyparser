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

import functools
import inspect
import itertools
import os
import re
import sys
import types
from collections.abc import Callable

import rich_click as click
from rich import print as rprint

__version__ = "0.2.1"
__all__ = ("set_env", "set_epilog", "set_groups", "parse", "flag")


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


def handled_type(atype, htype="m"):
    """
    Get the type of an argument.

    :param atype: (type) a type
    :param htype: (str) m for subtype and s for subtype
    :return: (type) the type of an argument
    """
    dic_type = {
        "m": [int, float, bool, str, tuple],
        "s": [int, float, str, Ellipsis],
    }
    if isinstance(atype, types.GenericAlias):
        atype = atype.__mro__[0]
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
        self.is_flag = False
        self.const = "$$void$$"
        self.type = self.set_type(arg_type)
        self.pgroup = self.get_parser_group()
        self.multiple = False

    def __eq__(self, arg):
        """
        Compare to Argument object and say if they are equal.

        :param arg: (Argument object)
        """
        return (
            self.name == arg.name
            and self.default == arg.default
            and self.help == arg.help
            and self.short_name == arg.short_name
            and self.choice == arg.choice
            and self.value == arg.value
            and self.is_flag == arg.is_flag
            and self.const == arg.const
            and self.type == arg.type
            and self.pgroup == arg.pgroup
        )

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
        if arg_type == inspect._empty:
            return inspect._empty
        if handled_type(arg_type):
            if arg_type is bool:
                self.is_flag = True
            check_subtype(arg_type, self)
            return arg_type
        if isinstance(arg_type, type):
            msg = "Not handled type %s" % arg_type.__name__
        else:
            msg = "unknown type %s" % str(arg_type)
        message(msg, self, "e")
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

    def click_type(self):
        """
        :return: (type)
        """
        if isinstance(self.choice, list):
            # TODO check if the type of choices correspond to the type of
            # the argument
            if self.type != str:
                message("Choices will be converted to str", self, "w")
            return click.Choice(list(map(str, self.choice)))
        elif self.type is bool:
            return click.BOOL
        elif isinstance(self.type, types.GenericAlias):
            if (
                self.type.__name__ == "tuple"
                and self.type.__args__[1] is not Ellipsis
            ):
                return click.Tuple(self.type.__args__)
            else:
                self.multiple = True
                return self.type.__args__[0]
        else:
            return self.type

    def click_narg(self):
        if not isinstance(self.type, types.GenericAlias):
            return None
        elif (
            self.type.__name__ == "tuple"
            and self.type.__args__[1] is not Ellipsis
        ):
            return len(self.type.__args__)
        else:
            return 1

    def get_parser_group(self) -> str:
        """
        Get the group name of the wanted argument.

        :return: the name of the group
        """
        for key in groups.keys():
            if self.name in groups[key]:
                if "help" in groups[key]:
                    return key
                else:
                    return key
        if self.default == inspect._empty:
            return required_title
        else:
            return optionals_title


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
        return (
            self.args == parser.args
            and self.order == parser.order
            and self.help == parser.help
        )

    def init_args(self):
        """
        Initiate the creation the argument of interest.
        """
        sign = inspect.signature(self.func).parameters
        if "help" not in sign.keys():
            dic_args = {
                k: Argument(
                    k,
                    sign[k].default,
                    sign[k].annotation
                    if sign[k].annotation != inspect._empty
                    else str,
                )
                for k in sign.keys()
            }
            dic_args["help"] = Argument("help", "help", str)
            return dic_args, list(sign.keys())
        else:
            print(
                "error: argument conflict, help argument cannot be set in"
                "the parsed function"
            )
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
                doc = itertools.takewhile(
                    lambda x: delim not in x and header not in x, doc
                )
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

    def get_short_name(self):
        """
        Get the short param name of self.args
        """
        param_names = sorted(list(self.args.keys()))
        if "help" in param_names:
            self.args["help"].short_name = "h"
            selected_param = ["h"]
            del param_names[param_names.index("help")]
        else:
            selected_param = []
        for param in param_names:
            sn = get_name(param, selected_param)
            self.args[param].short_name = sn
            selected_param.append(sn)

    def set_constrain(self, choices: dict[str, str | list]):
        """
        Set the contains for every param in self.args.

        :param choices: (dictionary of values) the constrains
        """
        for marg in choices.keys():
            if marg in self.args.keys():
                if isinstance(choices[marg], str) and choices[marg] not in [
                    "dir",
                    "file",
                ]:
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

    def create_click_group(self):
        """
        Create a click group for the parser.
        """
        dic_grp = {}
        for _, arg in self.args.items():
            if arg.pgroup in dic_grp:
                dic_grp[arg.pgroup].append(f"--{arg.name}")
            else:
                dic_grp[arg.pgroup] = [f"--{arg.name}"]
        click.rich_click.OPTION_GROUPS = {
            sys.argv[0]: [
                {"name": key, "options": dic_grp[key]} for key in dic_grp
            ]
        }

    def update_param(self):
        """
        Update if needed the type and the help of every args.
        """
        if self.func.__doc__:
            doc = filter(
                lambda x: pd1 in x and pd2 in x,
                re.split("[\n\r]", self.func.__doc__),
            )
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
                    print(
                        "Error : The name '%s' must have at least one of the"
                        "following symbols [A-Za-z]" % key
                    )
                    exit(1)
            pname[key] = n
            if n not in tmp:
                tmp.append(n)
            else:
                print(
                    "Error %s after removing symbols not in [A-Za-z0-9]"
                    "is already defined" % key
                )
                exit(1)
    global groups
    groups = arg_groups if arg_groups is not None else {}
    global lpg_name
    global grp_order
    grp_order = order
    lpg_name = pname
    global optionals_title
    optionals_title = help_name


def get_name(name, list_of_name, size=1):
    """

    :param name: (string) the param name
    :param list_of_name: (string) the list of param name
    :param size: (int) the size of the name used
    :return: (string) the param name selected
    """
    if size == len(name):
        return name
    elif name[0:size] not in list_of_name:
        return name[0:size]
    elif name[0:size].upper() not in list_of_name:
        return name[0:size].upper()
    else:
        return get_name(name, list_of_name, size=size + 1)


def check_subtype(argtype: type | types.GenericAlias, arg: Argument):
    """
    check if the subtype is supported.

    :param argtype: a type or list object
    :param arg: an Argument
    """
    if isinstance(argtype, types.GenericAlias):
        if not all(handled_type(t, "s") for t in argtype.__args__):
            message(
                "unknown %s subtype of %s"
                % (argtype.__args__, argtype.__name__),
                arg,
                "e",
            )
            exit(1)


def add_option(option: Argument, func: Callable) -> Callable:
    """
    Add an option to the function used to create the CLI.

    :param option: a lazyparser argument
    :param func: the function used to create a CLI
    :return: The function func decorated with click.option()
    """
    args = (
        (f"--{option.name}", f"-{option.short_name}")
        if len(option.name) > 1
        else (f"--{option.name}",)
    )
    kwargs = dict(
        nargs=option.click_narg(),
        type=option.click_type(),
        is_flag=option.is_flag,
        show_default=False,
        required=True,
        help=option.help,
        multiple=option.multiple,
    )
    if option.default != inspect._empty:
        kwargs["default"] = option.default
        kwargs["required"] = False
        kwargs["show_default"] = True
    func = click.option(
        *args,
        **kwargs,
    )(func)

    return func


def init_parser(lp: Lazyparser, func: Callable):
    """
    Create the parser using click.

    :param lp: the parsed arguments
    :param func: the function used to create a CLI
    :return: The function func decorated with click.option()
    """
    func.__doc__ = lp.description()
    for arg in lp.get_order()[::-1]:
        func = add_option(lp.args[arg], func)
    lp.create_click_group()
    func = click.command(epilog=epi)(func)
    return func


def message(
    sentence: str, argument: Argument, type_m: str | None = None
) -> str:
    """
    Return a message in the correct format.

    :param sentence: (string) the message we want to return.
    :param argument: (Argument object) a Lazyparser argument.
    :param type_m: (string or None) the type of the message to display
    :return: (string) the message in a correct format.
    """
    name = "[green]" + os.path.basename(sys.argv[0]) + "[/green]"
    sentence = re.sub(r"\s+", " ", sentence)
    sentence = "[blue] argument %s[/blue]: " % argument.gfn() + sentence
    if type_m not in ["w", "e"]:
        return sentence
    elif type_m == "w":
        rprint(name + ":[orange3] warning [/orange3]: " + sentence)
    else:
        rprint(name + ":[red] error [/red]: " + sentence)


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
            func = init_parser(lazyparser, function)
            return func()

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
