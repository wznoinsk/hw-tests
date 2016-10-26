===============================================
Tempest Integration of OpenStack Hardware Tests
===============================================

This repository contains hardware-dependant Tempest tests for OpenStack.

Features
--------

The tests validate the following features:

* PCI Passthrough

Installation
------------

To install system-wide into site packages:

    $ sudo pip install git+https://github.com/wznoinsk/hw-tests

Usage
-----

With Tempest tox:
    $ tox -eall-plugin hw_tests

