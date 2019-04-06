Lazyparser
==========

Lazyparser is a small module that allow to automatize the creation of command-line interfaces.
For this purpose it uses `argparse <https://docs.python.org/3.5/library/argparse.html>`_ developped by  by Steven J. Bethard.

Examples
--------

Without docstring
~~~~~~~~~~~~~~~~~

Let's say you have a function ``print_word`` That prints two words. To create a command line interface, you can simply type this in a file ``example.py``

.. code:: python

	import lazyparser as lp

	@lp.parse
	def print_word(a, b):
		print(a)
		print(b)

	if __name__ == "__main__":
		print_word()


Then you can run ``example.py`` by typing:

.. code:: Bash

	python example.py -h # to display the help of your program
	#usage: example.py [-h] -b B -a A
	#
	#optional arguments:
	#  -h, --help   show this help message and exit
	#
	#required argument:
	#  -b B, --b B  (str) param b
	#  -a A, --a A  (str) param a
	python example.py -a hello -b word
	# hello
	# word

As you can see, if there is no docstring in the decorated ``print_word`` function, the type of every parameters is set to `str`.  In addition, the **long names of the arguments for the parser** (defined with ``--`` in a command line) correspond to the **parameter names of the parsed function**. The sorth names (called with ``-`` in the command line interface) are computed on the fly and corresponds to the first letter(s) of the parameters to which they refer.
A default help message is generated for every parameter of the decorated function but don't explains what the parameter corresponds to.
To better control what the help message will display you can write a docstring in the decorated function.

With docstring
~~~~~~~~~~~~~~

Lazyparser automatize the creation of command-line interfaces by taking advantage of the docstring in the decorated function.
By default, lazyparser parse the docstring in `PyCharm <https://www.jetbrains.com/pycharm/>`_ (A Python IDE) format.

Example: (file ``example.py``)

.. code:: python

	import lazyparser as lp

	@lp.parse
	def mutliplication(a, b):
	    """
	    Mutiply a by b

	    :param a: (float) a number a
	    :param b: (float) a number b
	    """
	    return a * b


	if __name__ == "__main__":
	    v = mutliplication()
	    print(v)

Then you can run ``example.py`` by typing:

.. code:: Bash

	python example.py -h # to display the help of your program
	#usage: example.py [-h] -b B -a A
	# Mutiply a by b
	#
	# optional arguments:
	#   -h, --help   show this help message and exit
	#
	# required argument:
	#   -a A, --a A  (float) a number a
	#   -b B, --b B  (float) a number b
	python example.py -a 8.3 -b 7.2
	# 59.76

Customize the docstring environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are not a fan of pycharm docstrings you can set your own docstring environment by using the function ``set_env`` 

the function ``set_env`` takes 3 arguments :

	* ``delim1`` : the string preceding the definition of a parameter. *:param* is default in pycharm docstrings. This parameters can be set to an empty docstring if nothing precedes the parameter name.
	* ``delim2`` : the string that comes just after the name of the parameter. It **MUST** be defined and can't be an empty string or a space, tabulation, etc...
	* ``hd`` : This corresponds to an header preceding the argument name.

.. note:: 

	The text set before the parameters definition (or the parameters definition header) is considerated as being a part of the description of the function.
	
	
.. warning::

	The type of the parameters in the docstring must be surrounded by parentheses so that the lazyparser can interpret them.
	
Here is an example of how using ``set_env``

.. code:: python

	# code in example.py file
	import lazyparser as lp
	
	lp.set_env('', ':', "KeywordArgument")


	@lp.parse
	def mutliplication(a, b):
	    """
	    Mutiply a by b
		
		KeywordArgument
			 a : (float) a number a
			 b : (float) a number b
	    """
	    return a * b

	if __name__ == "__main__":
	    v = mutliplication()
	    print(v)


Define the type of parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the function docstring
_________________________

Lazyparser can handle different type of parameters:

	* ``int`` 
	* ``float`` 
	* ``Function`` : a lazyparser type representing user defined functions or buildin functions.
	* ``bool `` 
	* ``str`` : default type if nothing is specified in the function docstring
	*  ``FileType("o")`` : The argparse FileType. 'o' corresponds to the opening mode : same as you can use with open. It will give you an file object in the decorated function after parsing.  
	* ``List`` : A list object used to handle lists.

The ``List`` takes two parameters :

	1. ``size`` : The size of the list
	2. ``vtype`` : The type of the list. It must be one of the following types : 

		* ``int`` 
		* ``float`` 
		* ``Function`` 
		* ``bool `` 
		* ``str`` 
		*  ``FileType`` 

``List``don't handle ``List`` subtype !


.. warning::

	The type of the parameter can't be a ``tuple`` or a ``list``. Use the type ``List`` for that.


An example of ``List`` usage :
############################## 


.. code:: python

	# code in example.py file
	import lazyparser as lp


	@lp.parse
	def mutliplication(a):
	    """
	    Sum up the numbers given in a
		
		:param a : (List(vtype=float)) a list of numbers
	    """
	    return sum(a)

	if __name__ == "__main__":
	    v = mutliplication()
	    print(v)
		
Defining a list without any size allows you to give as many data as you want after the ``-a`` in the command line interface. Those data must be separated by a space

.. code:: bash

	python example.py -a 1 2 3 20
	# 26

An example of ``Function`` usage :
################################## 



.. code:: python

	# code in example.py file
	import lazyparser as lp


	@lp.parse
	def apply_a(a):
	    """
	    Apply the a function to the number 10.

		:param a : (Function) a function
	    """
	    return a(10)

	if __name__ == "__main__":
	    v = apply_a()
	    print(v)


.. code:: bash

	python example.py -a "lambda x: x - 5"
	# 5

As you can see if you define a lambda function you must surround its definition by quotes. It also works with buildin functions like``sum``.
You can also define **a** ``List`` **of**  ``Functions`` as described below :



.. code:: python

	# code in example.py file
	import lazyparser as lp


	@lp.parse
	def apply_a(a):
	    """
	    Apply every functions in a to the number 10.

		:param a : (List(vtype=Function)) a list of functions
	    """
		for f in a:
			print(f(10))

	if __name__ == "__main__":
	    apply_a()


.. code:: bash

	python example.py -a "lambda x: x - 5" "lambda x: x * 2"
	# 5
	# 20


An example of ``FileType`` usage :
##################################


Writting in file :

 .. code:: python

	# code in example.py file
	import lazyparser as lp


	@lp.parse
	def hello(a):
	    """
	    write 'hello world' in the file a

		:param a : (FileType('w')) a file
	    """
		a.write("hello world")

	if __name__ == "__main__":
	    hello()
		

.. code:: bash

	python example.py -a "hello.txt" # this will create a file 'hello.txt' containing 'hello world' in it.


Reading a file :

 .. code:: python

	# code in example.py file
	import lazyparser as lp


	@lp.parse
	def read(a):
	    """
	    Print the content of a file a.

		:param a : (FileType('r')) a file
	    """
		print(a.readlines())
		

	if __name__ == "__main__":
	    read()
		

.. code:: bash

	python example.py -a "hello.txt" # this will display the content of 'hello.txt' file.
	#hello world

.. note::

	You can also handle a list of ``FileType`` object by putting ``(List(vtype=FileType('w'))`` in a parameter description in the docstring of the parsed function.


In the function signature
_________________________


Lazyparser can interpret the type of parameter given in function signature. If the type of a parameter is given both in the docstring and the signature of the parsed function, **the type given in the signature will be used.**



Example with the multiply function:


.. code:: python

	import lazyparser as lp

	@lp.parse
	def mutliplication(a : float, b : float):
	    """
	    Mutiply a by b

	    :param a: a number a
	    :param b: (decimal number) a number b
	    """
	    return a * b


	if __name__ == "__main__":
	    v = mutliplication()
	    print(v)



.. code:: Bash

	python example.py -a 10 -b "lol"
	# usage: command.py [-h] -a [A] -b [B]
	# command.py: error: argument -b/--b: invalid float value: 'lol'

Lazyparser handle the type given in the function signature first. If a type is given in the function signature for a parameter, no type is needed in the docstring for this parameter.

It also works with ``List``, ``Function`` and ``FileType`` objects.


.. code:: python

	import lazyparser as lp
	from lazyparser import List, Function, FileType


	@lp.parse
	def apply_func(values : List(vtype=float), func : Function, afile : FileType('w')):
	    """
	    apply the function b to every element in values an write the results in afile.

	    :param values: list of float 
	    :param func: An amazing function
		:param afile: A super file
	    """
	    for v in values:
			afile.write("%s\n" % func(v))
		afile.close()


	if __name__ == "__main__":
	    apply_func()
 
.. code:: Bash

	python example.py -v 10 20 30 40 -f "lambda x : x * 2" -a result.txt # create a file result.txt containing 20 40 60 80.


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

.. warning::

	Unfortunatly, you can't constrain parameters corresponding to a function. 


.. note:: 

	Those constraints alos apply to parameter having a ``List`` type. For example a constrain of ``a=[1, 2]`` in a parameter ``a`` will ensure that every element given in the command-line interface for ``a`` is 1 or 2.
	
	
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
	# usage: command.py [-h] -v {0,1,2,3,4} [{0,1,2,3,4} ...]
	# command.py: error: argument -v/--values: invalid choice: 10.0 (choose from 0, 1, 2, 3, 4)
	python example.py -v 1 2 3 4
	# 10

.. code:: python

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
	python command.py -v 10 20 31
	# usage: command.py [-h] -v VALUES [VALUES ...]
	# command.py: error: argument -v/--values: invalid choice 31.0: it must respect : values % 2 == 0


Flag
~~~~

Sometimes, you only want to call an argument without giving it a value when calling your program. For example you want to multiply ``a`` by ``b`` if ``-t (or --time)`` is present in the command line or add them otherwise.
This can be done using the flag decorator.

Here is an example : 

.. code:: python

	import lazyparser as lp
	from lazyparser import Function


	@lp.flag(times=lambda x, y: x * y)
	@lp.parse
	def flag_func(a: float, b: float, times : Function = lambda x, y: x + y):
		"""

		:param a: a number a
		:param b: a number b
		"""
		return times(a, b)


	if __name__ == "__main__":
		v = flag_func()
		print(v)

.. code:: Bash

	python example.py -a 10 -b 2 -t
	# 20
	python example.py -a 10 -b 2
	# 12

As you can see, if ``times`` is set in the command line, the function defined in flag applies otherwise it's the default values.

.. warning::

	If you want to use a parameter as a flag, you must give it a default value along with it's flag values.








