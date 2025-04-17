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
import re
import sys
import types
from collections.abc import Callable
from typing import Any

import rich_click as click
from rich import print as rprint
from rich.panel import Panel

__version__ = "0.3.2"
__all__ = (
    "set_env",
    "set_epilog",
    "set_groups",
    "parse",
    "set_standalone_mode",
    "set_version",
)


#####################################
# sets the docstring environment
PD1 = ":param"  # param delimiter 1
PD2 = ":"  # param delimiter 2
STD_MODE = True  # Boolean indicating if the standalone mode is enabled
HEADER = ""  # header of arguments
TAB = 4  # number of spaces composing tabulations
EPI = None  # epilog for the parser
GROUPS = {}  # the groups of arguments
LPG_NAME = {}  # the name of the parser used
PROG_VERSION = None  # The version of program where lazyparser is used
FORBIDDEN = ["help", "h"]
OPTIONAL_TITLE = "Optional arguments"
REQUIRED_TITLE = "Required arguments"
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


def is_click_type(atype):
    """
    Check if the atype is a click type.

    :param atype: (type) a type
    :return: (bool) True if the type is a click type, False otherwise
    """
    try:
        res = issubclass(atype, click.Path.__mro__[1])
        if res:
            return True
    except TypeError:
        res = issubclass(type(atype), click.Path.__mro__[1])
        if res:
            return True
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
        self.short_name: str | None = None
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
            if arg_type is bool or arg_type is click.BOOL:
                if self.default == inspect._empty:
                    self.default = False
                elif self.default != False:
                    self.default = False
                    message("Default value set to False", self, "w")
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
            n = (
                "'[bold cyan]--%s[/bold cyan]' "
                + "/ '[bold green]-%s[/bold green]'"
            )
            name_arg = n % (
                self.name,
                self.short_name,
            )
        else:
            name_arg = "'[bold cyan]--%s[/bold cyan]'" % self.name
        return name_arg

    def click_type(self):
        """
        :return: (type)
        """
        if self.type is bool:
            return click.BOOL
        elif isinstance(self.type, types.GenericAlias):
            if self.type.__name__ == "tuple" and len(self.type.__args__) == 1:
                return click.Tuple(self.type.__args__)
            elif (
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
        elif self.type.__name__ == "tuple" and len(self.type.__args__) == 1:
            return 1
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
        for key in GROUPS.keys():
            if self.name in GROUPS[key]:
                if "help" in GROUPS[key]:
                    return key
                else:
                    return key
        if self.default == inspect._empty:
            return REQUIRED_TITLE
        else:
            return OPTIONAL_TITLE


class Lazyparser(object):
    """
    Lazyparser class.
    """

    def __init__(self, function, click_type):
        """
        Initialization with a function.

        :param function: (function) a function
        :param click_type: (dictionary) the click dtype
        """
        self.func = function
        self.args = self.init_args()
        self.help = self.description()
        self.update_param()
        self.get_short_name()
        self.set_constrain(click_type)

    def __eq__(self, parser):
        """
        Compare to parser and say if they are the same. \
        Note that the functions defining the two Lazyparser object \
        can be different but if those function have the same signature \
        this function will return True as they will store the same arguments.

        :param parser: (Lazyparser object)
        :return: (bool)
        """
        return self.args == parser.args and self.help == parser.help

    def init_args(self):
        """
        Initiate the creation the argument of interest.
        """
        sign = inspect.signature(self.func).parameters
        if any([x in sign.keys() for x in FORBIDDEN]):
            bad = [x for x in FORBIDDEN if x in sign.keys()]
            msg = (
                f"argument conflict, {bad} argument(s) cannot be set in"
                + " the parsed function"
            )
            message(msg, None, "e")
            exit(1)
        else:
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
            tmp = {"help": Argument("help", "help", str)}
            if PROG_VERSION:
                tmp["version"] = Argument("version", "version", str)
            return tmp | dic_args

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
            if PD1 == "":
                delim = PD2
            else:
                delim = PD1
            if not HEADER:
                doc = itertools.takewhile(lambda x: delim not in x, doc)
            else:
                doc = itertools.takewhile(
                    lambda x: delim not in x and HEADER not in x, doc
                )
            for line in doc:
                if line[0:TAB].strip() == "":
                    line = line[TAB:]
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

    def set_constrain(self, click_type: dict[str, Any]):
        """
        Set the contains for every param in self.args.

        :param click_type: (dictionary of values) the constrains as click type
        """
        for marg in click_type.keys():
            if marg in self.args.keys():
                if is_click_type(click_type[marg]):
                    if (
                        (
                            isinstance(click_type[marg], click.IntRange)
                            and self.args[marg].type != int
                        )
                        or (
                            isinstance(click_type[marg], click.FloatRange)
                            and self.args[marg].type != float
                        )
                        or (
                            isinstance(click_type[marg], click.Choice)
                            and self.args[marg].type != str
                        )
                    ):
                        message(
                            f"click type {click_type[marg]} incompatible "
                            + f"with {self.args[marg].type}, "
                            + "click type will be applied",
                            self.args[marg],
                            "w",
                        )
                    self.args[marg].type = click_type[marg]
                else:
                    message(
                        f"Unknown click type {click_type[marg]}",
                        self.args[marg],
                        "e",
                    )
                    exit(1)

    def create_click_group(self):
        """
        Create a click group for the parser.
        """
        if GROUPS:
            dic_grp = {k: [] for k in GROUPS}
        else:
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
        Update if needed the help of every args.
        """
        if self.func.__doc__:
            doc = filter(
                lambda x: PD1 in x and PD2 in x,
                re.split("[\n\r]", self.func.__doc__),
            )
            for line in doc:
                if PD1 != "":
                    flt = list(filter(None, line.split(PD1)[1].split(PD2)))
                else:
                    flt = list(filter(None, line.split(PD2)))
                flt = [word for word in flt]
                flt[0] = flt[0].strip()
                if flt[0] in self.args.keys():
                    if len(flt[1:]) > 1:
                        flt_desc = PD2.join(flt[1:])
                    else:
                        flt_desc = flt[1]
                    self.args[flt[0]].help = re.sub(
                        " +", " ", flt_desc.strip()
                    )


def set_standalone_mode(standalone_mode: bool = True):
    """
    change the standalone mode

    :param standalone_mode: True to enable the standalone mode false else
    """
    if isinstance(standalone_mode, bool):
        global STD_MODE
        STD_MODE = standalone_mode


def set_version(version: str | None = None):
    """
    Set the version of the program where lazyparser is used.

    :param version: (str) the version of the program.
    """
    if isinstance(version, str):
        global PROG_VERSION
        PROG_VERSION = version
        FORBIDDEN.append("version")


def set_env(delim1=":param", delim2=":", hd="", tb=4):
    """
    Change the param delimiters.

    :param delim1: (string) param delimiter 1
    :param delim2: (string) param delimiter 2
    :param hd: (string) the header of parameter
    :param tb: (int) the number of space/tab that bedore the docstring
    """
    if isinstance(tb, int):
        global TAB
        TAB = tb
    else:
        TAB = 4
    args = [delim1, delim2, hd]
    if sum([not isinstance(a, str) for a in args]) > 0:
        message("delim1 and delim2 must be strings", None, "e")
        exit(1)
    for i in range(len(args)):
        args[i] = args[i].replace("\n", "")
        args[i] = args[i].replace("\r", "")
        args[i] = args[i].replace("\t", "")
        args[i] = args[i].replace(" ", "")
    if not delim2:
        message("Bad delim2 definition", None, "e")
        exit(1)
    else:
        global PD1
        PD1 = delim1
        global PD2
        PD2 = delim2
        global HEADER
        HEADER = hd


def set_epilog(epilog):
    """
    Allow the user to define an epilog for the parser.

    :param epilog: (str) a parser epilog.
    """
    if isinstance(epilog, str):
        global EPI
        EPI = epilog


def set_groups(arg_groups=None):
    """
    Change the name of the argument groups.

    :param arg_groups: (dictionary of list of string) links each arguments to \
    its groups.
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
                    msg = (
                        "The name '%s' must have at least one of the"
                        + "following symbols [A-Za-z]"
                    ) % key
                    message(msg, None, "e")
                    exit(1)
            pname[key] = n
            if n not in tmp:
                tmp.append(n)
            else:
                msg = (
                    "%s after removing symbols not in [A-Za-z0-9]"
                    + "is already defined"
                ) % key
                message(msg, None, "e")
                exit(1)
    global GROUPS
    GROUPS = arg_groups if arg_groups is not None else {}
    global LPG_NAME
    LPG_NAME = pname
    global OPTIONAL_TITLE
    OPTIONAL_TITLE = help_name


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
    args = (f"--{option.name}", f"-{option.short_name}")
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
        **kwargs,  # type: ignore
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
    for arg in lp.args:
        if arg not in FORBIDDEN:
            func = add_option(lp.args[arg], func)
    lp.create_click_group()
    if PROG_VERSION:
        func = click.version_option(PROG_VERSION)(func)
    func = click.help_option("-h", "--help")(func)
    if STD_MODE:
        func = click.command(epilog=EPI)(func)
    else:
        func = click.command(epilog=EPI)(func).main(standalone_mode=False)
    return func


def message(
    sentence: str, argument: Argument | None, type_m: str | None = None
) -> None:
    """
    Return a message in the correct format.

    :param sentence: (string) the message we want to return.
    :param argument: (Argument object) a Lazyparser argument.
    :param type_m: (string or None) the type of the message to display
    :return: (string) the message in a correct format.
    """
    sentence = re.sub(r"\s+", " ", sentence)
    if argument is not None:
        sentence = argument.gfn() + " " + sentence
    if type_m not in ["w", "e"]:
        rprint(sentence)
    elif type_m == "w":
        rprint(
            Panel(
                sentence,
                title="Warning",
                border_style="orange3",
                title_align="left",
            )
        )
    else:
        rprint(
            Panel(
                sentence, title="Error", border_style="red", title_align="left"
            )
        )
        exit(1)


def parse(
    func: Callable | None = None, **kwargs
) -> Callable[..., Callable[[], Any]]:
    """
    Create the parser.

    :param func: (function) the function of interest
    :param kwargs: (dictionary) the named arguments
    :return: (function) wrap
    """

    def wrap(function: Callable) -> Callable[[], Any]:
        """
        Wrapper of the function ``function``.

        :param function: (function) the function to wrap
        :return: (function) the method calling `` function``.
        """

        @functools.wraps(function)
        def call_func(*args, **kw):
            """
            Call the function ``self.func`` and return it's result.

            :return: the result of the function ``self.func``
            """
            lazyparser = Lazyparser(function, kwargs)
            func = init_parser(lazyparser, function)
            if STD_MODE:
                return func(*args, **kw)
            else:
                return func

        return call_func

    if func is None:
        return wrap
    return wrap(func)
