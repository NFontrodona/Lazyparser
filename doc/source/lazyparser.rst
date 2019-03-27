Lazyparser
==========

Lazyparser is a small module that allow to automatize the creation of command-line interfaces.
For this purpose it uses `argparse <https://docs.python.org/3.5/library/argparse.html>`_ developped by  by Steven J. Bethard.

Example
--------

Without docstring
~~~~~~~~~~~~~~~~~

Let's say you have a function ``print_word`` That prints two words. To create a command line interface, you can simply type this in a file ``example.py``

.. code:: python

	import lazyparser

	@lazyparser.wrapper
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

With docstring
~~~~~~~~~~~~~~

Lazyparser automatize the creation of command-line interfaces by taking advantage of the docstring in the decorated function.
For the moment it only parse `PyCharm <https://www.jetbrains.com/pycharm/>`_ (A Python IDE)  formated docstrings.

Example: (file ``example.py``)

.. code:: python

	import lazyparser

	@lazyparser.wrapper
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


Constraints
~~~~~~~~~~~

You can constrain the values that an argument with:

.. code:: python
	@lazyparser.wrapper(a=[1, 2]) # the parameter a must be equal to 1 or 2
	@lazyparser.wrapper(a=["a", "b"]) # the parameter a must be equal to "a" or "b"
	@lazyparser.wrapper(a="file") # the parameter a must be an existing file
	@lazyparser.wrapper(a="dir") # the parameter a must be an existing dir
	@lazyparser.wrapper(a="2 < a < 5") # a must be greater than 2 and lower than 5
