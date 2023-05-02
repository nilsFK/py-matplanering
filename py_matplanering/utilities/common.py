#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
common.py is common low-level functionality
and should not import anything except for
built in packages. It should contain
reusable functions, types and similar which
does not heavily depend on implementation
details of the software.
"""
import ntpath
import codecs
import re
import sys
import decimal
import copy

from typing import Any, Callable

class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)
    def __repr__(self):
        return repr(self.__dict__)

def as_obj(to_obj: dict):
    return Struct(**to_obj)

def as_dict(from_obj):
    return from_obj.__dict__

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

def is_decimal(data: Any):
    return isinstance(data, decimal.Decimal)

def is_dict(data: Any):
    return isinstance(data, dict)

def is_Struct(data: Any):
    return isinstance(data, Struct)

def is_list(data: Any):
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

def nvl(val, replacement=''):
    return val if val is not None else replacement

class Consumable():
    def __init__(self, consumable: Any, consumption_quota: int=None):
        self.consumable = consumable
        self.consumption_quota = consumption_quota
        self.consumed_count = 0
        self.consumed = copy.copy(consumable)
        self.consumed.clear()
        if consumption_quota > len(consumable):
            raise Exception('Consumption quota (%s) exceeds items in consumable' % (self.consumption_quota))

    def consume(self, partial: list=None, callback: Callable=None) -> list:
        """ Consumes a partial either by partial parameter or by partial
            returned by callback. Returns list of consumed items. """
        if partial is not None and len(partial) == 0:
            raise Exception('Partial is empty and nothing can be consumed')
        if callback:
            partial = callback(self.consumable)
            if not isinstance(partial, list):
                raise Exception('Callback must return list of partial to be consumed')
        consumed_lst = []
        for x in partial:
            if self.consumption_quota and self.consumed_count >= self.consumption_quota:
                return self
            if x not in self.consumable:
                raise Exception('Attempting to consume %s which is not within consumables: %s' % (x, self.consumable))
            if isinstance(self.consumable, list):
                self.consumable.remove(x)
                self.consumed.append(x)
            if isinstance(self.consumable, set):
                self.consumable.discard(x)
                self.consumed.add(x)
            consumed_lst.append(x)
        self.consumed_count += len(consumed_lst)
        return consumed_lst

    def is_consumed(self, partial: Any) -> bool:
        return partial in self.consumed

    def is_all_consumed(self) -> bool:
        return self.consumption_quota - self.consumed_count == 0
    # def __len__(self):
        # return len(self.consumable)



