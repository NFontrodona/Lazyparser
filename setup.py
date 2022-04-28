#!/usr/bin/env python3

import setuptools
import lazyparser

with open("README.md", "r") as readfile:
    long_description = readfile.read()

setuptools.setup(
    name="lazyparser",
    version=lazyparser.__version__,
    author="Nicolas Fontrodona",
    author_email="nfontrodona@orange.fr",
    license="Apache License 2.0",
    description="Lazyparser automates the parsing of arguments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NFontrodona/Lazyparser",
    py_modules=["lazyparser"],
    tests_require=["pytest-cov"],
    install_requires=[
        "argparse>=1.4.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: Apache Software License  ",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.5",
)