# Documentation

Lazyparser is a small module that automates the creation of command-line
interfaces. For this purpose, it uses
[rich_click](https://github.com/ewels/rich-click).

## Basic usage

### Without docstring

Let's say you have a function `print_word` that prints two words. To
create a command line interface, you can simply type this in a file
`example.py`

``` python
import lazyparser as lp

@lp.parse
def print_word(a, b):
    print(a)
    print(b)

if __name__ == "__main__":
    print_word()
```

Then you can display the help of `example.py` by typing:

``` Bash
python example.py --help  # to display the help of your program
```

This will print the following message :

```Bash

 Usage: example.py --b STRING --a STRING

╭─ Optional arguments ─────────────────────────────────╮
│ --help  -h    Show this message and exit.            │
╰──────────────────────────────────────────────────────╯
╭─ Required arguments ─────────────────────────────────╮
│ *  --a  -a  TEXT  param a [required]                 │
│ *  --b  -b  TEXT  param b [required]                 │
╰──────────────────────────────────────────────────────╯
```

If there is no docstring in the decorated `print_word` function, the
type of every parameters is set to `str`. In addition, the **full names
of the parser arguments** (defined with `--`) correspond to the
**parameter names of the decorated function**. The short names (called
with `-`) are computed on the fly and correspond to the first letter of
the related parameter. For each parameter in the decorated function, a basic help message is auto-generated, though this default message provides minimal information about what each parameter actually does. To customize how the help
message will be displayed, you can write a docstring in the decorated
function.

### With docstring

Lazyparser automates the creation of command-line interfaces by taking
advantage of the **docstring** in the decorated function and **the type of the parameters** indicated in the function definition. By default,
lazyparser parses the docstring in
[PyCharm](https://www.jetbrains.com/pycharm/) (A Python IDE) format.

Example: (file `example.py`)

``` python
import lazyparser as lp

@lp.parse
def multiplication(a: float, b: float):
    """Multiply a by b

    :param a: a number a
    :param b: a number b
    """
    print(a * b)


if __name__ == "__main__":
    multiplication()
```

Then, you can display the help of `example.py` by typing:

``` Bash
$ python example.py -h # to display the help of your program
Usage: example.py --b FLOAT --a FLOAT

Multiply a by b

╭─ Optional arguments ─────────────────────────────────╮
│ --help  -h    Show this message and exit.            │
╰──────────────────────────────────────────────────────╯
╭─ Required arguments ─────────────────────────────────╮
│ *  --a  -a  FLOAT  a number a [required]             │
│ *  --b  -b  FLOAT  a number b [required]             │
╰──────────────────────────────────────────────────────╯
```

## Optional arguments

In the previous example, you can see that --a and --b are required arguments. To make an argument optional, you can give it a default value in the function definition. For example, if you want to make the argument --b optional, you can define it as follows:

```python
# same as above
@lp.parse
def multiplication(a: float, b: float = 5):
    """Multiply a by b

    :param a: a number a
    :param b: a number b
    """
    print(a * b)
# same as above
```

```Bash
$ python example.py --help
Usage: example.py --a FLOAT [--b FLOAT]

Multiply a by b

╭─ Optional arguments ─────────────────────────────────╮
│ --help  -h         Show this message and exit.       │
│ --b     -b  FLOAT  a number b [default: 5]           │
╰──────────────────────────────────────────────────────╯
╭─ Required arguments ─────────────────────────────────╮
│ *  --a  -a  FLOAT  a number a [required]             │
╰──────────────────────────────────────────────────────╯
```

## standalone mode

By default the standalone mode is enabled, this means that nothing can be executed after the call of the decorated function, for example this code won't print anything after "starting":

``` python
import lazyparser as lp

@lp.parse
def multiplication(a: float, b: float):
    """Multiply a by b

    :param a: a number a
    :param b: a number b
    """
    print("starting")
    return a * b


if __name__ == "__main__":
    v = multiplication() # nothing executed after this
    print(v)
```

``` Bash
$ python example.py -a 5 -b 10
starting
```

To make the code continue, you can disable the click standalone mode by using the `sandalone(False)` decorator

Example:

``` python
import lazyparser as lp

@lp.standalone(False)
@lp.parse
def multiplication(a: float, b: float):
    """Multiply a by b

    :param a: a number a
    :param b: a number b
    """
    print("starting")
    return a * b


if __name__ == "__main__":
    v = multiplication() # noting executed after this
    print(v)
```

``` Bash
$ python example.py -a 5 -b 10
starting
50.0
```

## Customize the docstring environment

If you are not a fan of Pycharm docstrings, you can set your own
docstring environment by using the decorator `docstrings`

the decorator `docstrings` can takes up to 4 arguments :

- `delim1` : the string preceding the definition of a parameter.
  *:param* is the default value. This parameter can be an empty
  docstring if nothing precedes the parameter name in the docstring of
  the decorated function.
- `delim2` : the string that comes right after the name of the
  parameter. It **MUST** be defined and can't be an empty string or a
  space, tabulation, etc... It's default value is `:`
- `header` : the header preceding the argument names. By default,
  corresponds to an empty string.
- `tab` : the number of spaces at the beginning of each line in the
  docstring. By default, it is equal to 4.

!!! note

    the text set before parameters definition (or the parameters definition header) is considered as being a part of the description of the function.


Here is an example of how to use `docstrings`

``` python
# code in example.py file
import lazyparser as lp

@lp.docstrings(delim1='', delim2=':', header="Arguments:")
@lp.parse
def multiplication(a: float, b: float):
    """
    Multiply a by b

    Arguments:
         a : a number a
         b : a number b
    """
    print(a * b)

if __name__ == "__main__":
    multiplication()
```

## Type of parameters

Lazyparser can handle different types of parameters (defined in the function definition):

- `int`
- `float`
- `bool`
- `str` : default type if nothing is specified in the function definition.
- `tuple` : A tuple object used to handle multiple values.

`tuple` type must have at least one subtype defined in the function definition.
For example, if we want to define a tuple with one integer, we can set the type `tuple[int]`

### Example of `tuple` usage :

``` python
import lazyparser as lp

@lp.docstrings(delim1="", delim2=":", header="Arguments:")
@lp.parse
def print_value(a: tuple[int]):
    """
    Display the parameter a

    :param a: The argument a
    """
    print(f"a = {a}")


if __name__ == "__main__":
    print_value()
```

Defining a tuple with an elipsis as the second type `tuple[int, ...]` allows you to give as many data as you by repeating `-a` in the command line interface. Here is an example:

```python
# same as above
def print_value(a: tuple[int, ...]):
# same as above
```

```console
$ python example.py -a 1 -a 2 -a 3 -a 20
a = (1, 2, 3, 20)
```


## Click types

You can use custom click types (see [this page](https://click.palletsprojects.com/en/stable/options/) instead of the simple ones that you give in the function signature. For example if you want to use the custom type `click.IntRange(0, 10)`, you can do so in the `lazyparser.parse` function using the following syntax:

``` python
@lazyparser.parse(param=click.IntRange(0, 10))
```
where `param` is the name of the parameter you want to use the custom type for.

!!! note

    the type of param given in the function signature should be `int` in this case otherwise you will get an warning telling you that the click type will be applied.


### Example:

``` python
import lazyparser as lp


@lp.parse(values=lp.click.IntRange(0, 10))
def print_value(values : int):
    """
    Print an input number between 0 and 10
    """
    print("Your number is", values)

if __name__ == "__main__":
    print_value()
```

```console
$ python example.py -v 15

Usage: example.py [OPTIONS]

Try 'example.py --help' for help
╭─ Error ────────────────────────────────────────────────────────────╮
│ Invalid value for '--values' / '-v': 15 is not in the range        │
│ 0<=x<=10.                                                          │
╰────────────────────────────────────────────────────────────────────╯

$ python example.py -v 8
Your number is 8
```

## Boolean flag

Sometimes, you only want to call an argument without giving it a value
when calling your program. This applies automatically and only for Booleanvalues

Here is an example :

``` python
import lazyparser as lp

@lp.parse
def flag_func(a: bool = False):
    """
    Give the value of the flag

    :param a: the boolean flag
    """
    print(f"value of a: {a}")


if __name__ == "__main__":
    flag_func()
```

```console
$ python example.py -a
value of a: True
$ python example.py
value of a: False
```

## Create an epilog

To add an epilog in the help of the parser simply use the decorator
`epilog`. This function must be called before the decorator `parse`.

```
@lp.epilog("my epilog")
@lp.parse
...
```

## Argument groups

By default, Lazyparser creates two groups of arguments:

> - `Optional arguments`
> - `Required arguments`

But, you may want to create argument groups with custom names. This can
be done with the decorator `groups` that takes a group name and a list of
options defined in the group. The order of groups given in the groups decorator will be the same as the order of group displayed in the help message.


This function must be called before the decorator `parse`.

### Example

Below, in an file named `example.py`. You can see a function that prints
the name and the first name of a user and also multiply two numbers:

``` python
import lazyparser as lp

@lp.groups(help=["help"], Numbers=["x", "y"], User=["first_name", "name"])
@lp.parse
def multiply(first_name: str, name: str, x: float, y: float):
    """Say hello name fist_name and multiply x by y.

    :param first_name: your first name
    :param name: your name
    :param x: a number x
    :param y: a number y
    """
    print(f"Hello {first_name} {name} !")
    print(f"{x} x {y} = {x * y}")


if __name__ == "__main__":
    multiply()
```

If you run:

``` bash
python example.py -h
```

It displays:

``` bash
Usage:
example.py
--y FLOAT --x FLOAT --name TEXT --first_name TEXT

Say hello name fist_name and multiply x by y.

╭─ help ───────────────────────────────────────────────╮
│ --help  -h    Show this message and exit.            │
╰──────────────────────────────────────────────────────╯
╭─ Numbers ────────────────────────────────────────────╮
│ *  --x  -x  FLOAT  a number x [required]             │
│ *  --y  -y  FLOAT  a number y [required]             │
╰──────────────────────────────────────────────────────╯
╭─ User ───────────────────────────────────────────────╮
│ *  --first_name  -f  TEXT  your first name           │
│                            [required]                │
│ *  --name        -n  TEXT  your name [required]      │
╰──────────────────────────────────────────────────────╯

```


## Version option

In order to have a option to display the version you can use the `version`
decoartor.

### Example

```python
import lazyparser as lp

@lp.version("1.0")
@lp.parse
def multiplication(a: float, b: float):
    """
    Multiply a by b

    :param a : a number a
    :param b : a number b
    """
    print(a * b)

if __name__ == "__main__":
    multiplication()
```

If you run:

```bash
$ python example.py -h
Usage: example.py --b FLOAT --a FLOAT

Multiply a by b

╭─ Optional arguments ─────────────────────────────────╮
│ --help     -h    Show this message and exit.         │
│ --version        Show the version and exit.          │
╰──────────────────────────────────────────────────────╯
╭─ Required arguments ─────────────────────────────────╮
│ *  --a  -a  FLOAT  a number a [required]             │
│ *  --b  -b  FLOAT  a number b [required]             │
╰──────────────────────────────────────────────────────╯
$ python example.py --version
example.py, version 1.0
```

!!! warning

    Your function cannot contain a parameter named `version` anymore.

## Using multiple decorators

You can use multiple decorators like `lp.version`, `lp.standalone`, `lp.groups` and `lp.docstrings` in any order with the exception of the `lp.parse` decorator which should be the first one to decorate your function.


```python
import lazyparser as lp

@lp.docstrings(delim1="-", delim2=":", header="@Args") # In any order (expect the first)
@lp.groups(values=["a", "b"], Help=["help"]) # In any order (expect the first)
@lp.version("1.0") # In any order (expect the first)
@lp.standalone(True) # In any order (expect the first)
@lp.parse # must be the first decorator
def multiplication(a: float, b: float):
    """
    Multiply a by b

    @Args
    - a : a number a
    - b : a number b
    """
    print(a * b)

if __name__ == "__main__":
    multiplication()
```
