# Update Notes

## version 0.4.0

* API changes for environment functions, they are now decorators
* Update usage display in help message
* Add a check to force ellipsis to be at the second position in tuple subtype

## version 0.3.2

* Add short help option name to display the help
* Add set_version function

## version 0.3.1

* Add set_standalone function to be able to disable click standalone mode

## version 0.3.0

* Lazyparser is now based on rich_click instead of argparse

## version 0.2.1

* Add support for typing.List for python 3.10

## version 0.2.0

* Lazyparser doesn't handle FileType and Function types anymore.

## version 0.1.1

* Fix list subtypes checking when defined in the function definition.
* The object `List` form **typing** package is now recognized by Lazyparser and automatically transformed in ``lazyparser.List`` object.
