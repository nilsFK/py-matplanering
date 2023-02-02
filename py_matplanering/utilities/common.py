#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
common.py is common low-level functionality
and should not import anything except for
built in packages.
"""
import ntpath
import codecs
import re
import sys
import decimal

class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)
    def __repr__(self):
        return repr(self.__dict__)

def as_obj(to_obj):
    return Struct(**to_obj)

def as_dict(from_obj):
    return from_obj.__dict__

def singleton(cls):
    obj = cls()
    # Always return the same object
    cls.__new__ = staticmethod(lambda cls: obj)
    # Disable __init__
    try:
        del cls.__init__
    except AttributeError:
        pass
    return cls

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def is_decimal(data):
    return isinstance(data, decimal.Decimal)

def is_dict(data):
    return isinstance(data, dict)

def is_Struct(data):
    return isinstance(data, Struct)

def is_list(data):
    return isinstance(data, list)

def is_unicode(s):
    return isinstance(s, str)

def decode(val):
    """Since we in most cases are not aware of
    the true encoding we try to decode it from
    utf-8, if that fails we decode it as latin-1,
    if that fails we return it as is.
    Note that we attempt decoding in this order
    because py-privatekonomi only works with
    utf-8 and latin-1
    """
    try:
        val = val.decode("utf-8")
    except:
        try:
            val = val.decode("latin-1")
        except:
            pass
    return val

def camelcase_to_underscore(name):
    """ CamelCase to camel_case """
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def underscore_to_camelcase(name):
    """ under_score to UnderScore """
    return ''.join(x.capitalize() or '_' for x in name.split('_'))
