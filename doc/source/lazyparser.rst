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

As you can see, if there is no docstring in the decorated ``print_word`` function, the type of every parameters is set to `str`.
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

customize the docstring environment
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


define the type of parameters
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


.. warning::

	The type of the parameter can't be a ``tuple`` or a ``list``. Use the type ``List`` for that.


In the function signature
_________________________


Lazyparser can interpret the type of parameter given in function signature. If the type of a parameter is given both in the docstring and the signature of the parsed function, **the type given in the signature will be use**

Example :  


Constraints
~~~~~~~~~~~

You can constrain the values that an argument with:

.. code:: python

	@lazyparser.wrapper(a=[1, 2]) # the parameter a must be equal to 1 or 2
	@lazyparser.wrapper(a=["a", "b"]) # the parameter a must be equal to "a" or "b"
	@lazyparser.wrapper(a="file") # the parameter a must be an existing file
	@lazyparser.wrapper(a="dir") # the parameter a must be an existing dir
	@lazyparser.wrapper(a="2 < a < 5") # a must be greater than 2 and lower than 5
