Lazyparser
==========

Lazyparser is a small module that automates the creation of command-line interfaces.
For this purpose, it uses `argparse <https://docs.python.org/3.7/library/argparse.html>`_ developped by Steven J. Bethard.

Examples
--------

Without docstring
~~~~~~~~~~~~~~~~~

Let's say you have a function ``print_word`` that prints two words. To create a command line interface, you can simply type this in a file ``example.py``

.. code:: python

    import lazyparser as lp

    @lp.parse
    def print_word(a, b):
        print(a)
        print(b)

    if __name__ == "__main__":
        print_word()


Then you can display the help of ``example.py`` by typing:

.. code:: Bash

    python example.py -h  # to display the help of your program

This will print the following message :

.. code:: Bash

    usage: example.py [-h] -a STR -b STR

    Optional arguments:
      -h, --help   show this help message and exit

    Required arguments:
      -a, --a STR  param a
      -b, --b STR  param b


If there is no docstring in the decorated ``print_word`` function, the type of every parameters is set to ``str``.  In addition, the **full names of the parser arguments** (defined with ``--``) correspond to the **parameter names of the decorated function**. The short names (called with ``-``) are computed on the fly and correspond to the first letter of the parameter to which they refer.
A default help message is generated for every parameter of the decorated function but it doesn't explain what the parameter corresponds to.
To better control what the help message will display, you can write a docstring in the decorated function.

With docstring
~~~~~~~~~~~~~~

Lazyparser automates the creation of command-line interfaces by taking advantage of the docstring in the decorated function.
By default, lazyparser parse the docstring in `PyCharm <https://www.jetbrains.com/pycharm/>`_ (A Python IDE) format.

Example: (file ``example.py``)

.. code:: python

    import lazyparser as lp

    @lp.parse
    def multiplication(a, b):
        """Multiply a by b

	    :param a: (float) a number a
	    :param b: (float) a number b
	    """
        return a * b


    if __name__ == "__main__":
        v = multiplication()
        print(v)

Then, you can display the help of ``example.py`` by typing:

.. code:: Bash

    python example.py -h # to display the help of your program

This displays the following message:

.. code:: Bash

    usage: example.py [-h] -a FLOAT -b FLOAT

    Multiply a by b

    Optional arguments:
      -h, --help     show this help message and exit

    Required arguments:
      -a, --a FLOAT  a number a
      -b, --b FLOAT  a number b


Customize the docstring environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are not a fan of Pycharm docstrings, you can set your own docstring environment by using the function ``set_env``

the function ``set_env`` takes 4 arguments :

    * ``delim1`` : the string preceding the definition of a parameter. *:param* is the default value. This parameter can be an empty docstring if nothing precedes the parameter name in the docstring of the decorated function.
    * ``delim2`` : the string that comes right after the name of the parameter. It **MUST** be defined and can't be an empty string or a space, tabulation, etc...
    * ``hd`` : the header preceding the argument names. By default, corresponds to an empty string.
    * ``tb`` : the number of spaces at the beginning of each line in the docstring. By default, it is equal to 4.

.. note::

    The text set before parameters definition (or the parameters definition header) is considered as being a part of the description of the function.


.. warning::

    The type of parameters in the docstring must be surrounded by parentheses so that lazyparser can interpret them.

Here is an example of how using ``set_env``

.. code:: python

    # code in example.py file
    import lazyparser as lp

    lp.set_env('', ':', "KeywordArgument")


    @lp.parse
    def multiplication(a, b):
        """
        Multiply a by b

        KeywordArgument
             a : (float) a number a
             b : (float) a number b
        """
        return a * b

    if __name__ == "__main__":
        v = multiplication()
        print(v)


Define the type of parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the function docstring
_________________________

Lazyparser can handle different types of parameters:

    * ``int``
    * ``float``
    * ``bool``
    * ``str`` : default type if nothing is specified in the function docstring.
    * ``List`` : A list object used to handle lists.

The ``List`` takes two parameters :

    1. ``size`` : The size of the list
    2. ``vtype`` : The type of the list. It must be one of the following types :

        * ``int``
        * ``float``
        * ``bool``
        * ``str``

``List`` don't handle ``List`` subtype !


.. warning::

    The type of parameters can't be ``tuple`` or ``list``. Use the type ``List`` for that.


An example of ``List`` usage :
##############################


.. code:: python

    # code in example.py file
    import lazyparser as lp


    @lp.parse
    def multiplication(a):
        """
        Sum up the numbers given in a

        :param a : (List(vtype=float)) a list of numbers
        """
        return sum(a)

    if __name__ == "__main__":
        v = multiplication()
        print(v)

Defining a list without any size allows you to give as many data as you want after the ``-a`` in the command line interface. Those data must be separated by a space

.. code:: bash

    python example.py -a 1 2 3 20
    # 26.0


In the function signature
_________________________


Lazyparser can interpret the type of parameters given in function signature. If the type of a parameter is given both in the docstring and in the signature, **the type given in the signature will be used.**


Example with the multiply function:

.. code:: python

    import lazyparser as lp

    @lp.parse
    def mutliplication(a : float, b : float):
        """
        Mutiply a by b

        :param a: (number) a number a
        :param b: (str) a number b
        """
        return a * b


    if __name__ == "__main__":
        v = mutliplication()
        print(v)



.. code:: Bash

    python example.py -a 10 -b "lol"
    # usage: example.py [-h] -a FLOAT -b FLOAT
    # example.py: error: argument -b/--b: invalid float value: 'lol'

Lazyparser handle the type given in the function signature first. If a type is given in the function signature for a parameter, no type is needed in the docstring for this parameter.

It also works with ``List`` objects.


It is possible to use the ``List`` type of the ``typing`` module! Lazyparser will automatically transform a ``typing.List`` object into a ``lazyparser.List`` object. With the ``typing.List`` class, you won't be able to limit the size of the list as it can be done with ``lazyparser.List(vtype=str, size=5)`` or simply ``List(5, str)``. Note that you can use the notation of the typing package in the docstring of the decorated function. Example ``:param a: (List[str]) my param``. With this method, it is also not possible to limit the length of the list.

.. code:: python

    import lazyparser as lp
    from typing import List


    @lp.parse
    def make_sum(values : List[float]): # typing typo
        """
        make the sum

        :param values: list of float
        """
        return sum(values)


    if __name__ == "__main__":
        print(make_sum())
 
.. code:: Bash

    python example.py -v 10 20 30 40


Constraints
~~~~~~~~~~~

You can constrain the values that a parameter can take with:

.. code:: python

    @lazyparser.parse(a=[1, 2]) # the parameter a must be equal to 1 or 2
    @lazyparser.parse(a=["a", "b"]) # the parameter a must be equal to "a" or "b"
    @lazyparser.parse(a="file") # the parameter a must be an existing file
    @lazyparser.parse(a="dir") # the parameter a must be an existing dir
    @lazyparser.parse(a="2 < a < 5") # a must be greater than 2 and lower than 5
    @lazyparser.parse(a="a%2 == 0") # a must be even


.. note:: 

    Those constraints also apply to parameters having a ``List`` type. For example, a constrain of ``a=[1, 2]`` in a list ``a`` will ensure that every element given in the command-line interface for ``a`` is 1 or 2.
	
	
Example:
________


.. code:: python

    import lazyparser as lp
    from lazyparser import List


    @lp.parse(values=range(5))
    def apply_sum(values : List(vtype=float)):
        """
       sum every values in ``values`` parameter.

        :param values: list of float
        """
        return sum(values)

    if __name__ == "__main__":
        v = apply_sum()
        print(v)


.. code:: Bash

    python example.py -v 10 20 30 40
    # usage: example.py [-h] -v LIST[FLOAT]
    # example.py: error: argument -v/--values: invalid choice: 10.0 (choose from 0, 1, 2, 3, 4)
    python example.py -v 1 2 3 4
    # 10.0

.. code:: python

    from lazyparser import List
    import lazyparser as lp

    @lp.parse(values="values % 2 == 0")
    def apply_sum(values: List(vtype=float)):
        """
       sum every values in ``values`` parameter.

        :param values: list of float
        """
        return sum(values)


    if __name__ == "__main__":
        v = apply_sum()
        print(v)


.. code:: Bash

    python example.py -v 10 20 31
    # usage: example.py [-h] -v LIST[FLOAT]
    # example.py: error: argument -v/--values: invalid choice 31.0: it must respect : values % 2 == 0

Flag
~~~~

Sometimes, you only want to call an argument without giving it a value when calling your program. For example, if we want to multiply ``a`` by ``b`` if ``-t (or --time)`` is present in the command line or add them otherwise.
This can be done using the decorator named flag.

Here is an example : 

.. code:: python

    import lazyparser as lp


    @lp.flag(times=True)
    @lp.parse
    def flag_func(a: float, b: float, times: bool = False):
        """

        :param a: a number a
        :param b: a number b
        """
        if times:
            return a * b
        else:
            return a + b


    if __name__ == "__main__":
        v = flag_func()
        print(v)

.. code:: Bash

    python example.py -a 10 -b 2 -t
    # 20.0
    python example.py -a 10 -b 2
    # 12.0

.. warning::

     If we want to use a parameter as a flag, you must give it a default value and a flag value.



Create an epilog
~~~~~~~~~~~~~~~~

To add an epilog in the help of the parser simply use the function ``set_epilog``. This function must be called before the decorator ``parse``.

.. code::

    lp.set_epilog("my epilog")


Argument groups
~~~~~~~~~~~~~~~

By default, Lazyparser creates two groups of arguments:

    * ``Optional arguments``
    * ``Required arguments``

But, you may want to create argument groups with custom names.
This can be done with the function ``set_groups`` that can takes the following arguments:

    * arg_groups : A dictionary having group names as keys and lists of argument names as values
    * order : A list of group names. Those names must be defined in ``arg_groups``
    * add_help : A boolean to indicate if you want a parameter named ``help`` that will display an help message in the command line interface.

This function must be called before the decorator ``parse``.

.. note::

    If ``set_groups(add_help=False)`` written in your script, then you won't be able to display an help message in you shell.


Example
_______

Below, in an file named ``example.py``. You can see a function that prints the name and the first name of a user and also multiply two numbers:

.. code:: python

    import lazyparser as lp

    lp.set_groups(arg_groups={"User_name": ["first_name", "name"],
                              "Numbers": ["x", "y"]})

    @lp.parse
    def multiply(first_name, name, x, y):
        """Say hello name fist_name and multiply x by y.

        :param first_name: (str) your first name
        :param name: (str) your name
        :param x: (float) a number x
        :param y: (float) a number y
        """
        print("Hello %s %s !" % (first_name, name))
        print("%s x %s = %s" % (x, y, x * y))


    if __name__ == "__main__":
        multiply()

If you run:

.. code:: bash

    python example.py -h

It displays:

.. code:: bash

    usage: example.py [-h] -f STR -n STR -x FLOAT -y FLOAT

    Say hello name fist_name and multiply x by y.

    Optional arguments:
      -h, --help            show this help message and exit

    User_name:
      -f, --first_name STR  your first name
      -n, --name STR        your name

    Numbers:
      -x, --x FLOAT         a number x
      -y, --y FLOAT         a number y

If you want to change the name of ``Optional arguments`` group, just call ``set_groups`` like this:

.. code::

    lp.set_groups(arg_groups={"User_name": ["first_name", "name"],
                              "Numbers": ["x", "y"],
                              "Group_help": ["help"]})

If you want the ``help`` argument to be in the user name groups, just call ``set_groups`` like this:

.. code::

    lp.set_groups(arg_groups={"User_name": ["help", "first_name", "name"],
                              "Numbers": ["x", "y"]})

.. note::

    Arguments in each group are displayed in the order of the decorated function.

