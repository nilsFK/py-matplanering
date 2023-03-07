#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
misc.py is common low-level functionality
and should not import anything except for
built in packages. It is an alternative to
common.py that is similar but may contain
functions that are heavily correlated with
implementation details of the software.
"""
# import ntpath
# import codecs
# import re
# import sys
# import decimal
# import copy
#
# from typing import Any, Callable

def make_event_quota(quota: dict):
    if quota.get('used') is None:
        quota['used'] = 0
    if quota.get('quota') is None:
        quota['quota'] = (quota['max'] - quota['min']) + 1
    # required props
    if any(v is None for v in [
        quota.get('min'),
        quota.get('max'),
        quota.get('time_unit')]):
        raise Exception('Required props must contain values: %s' % (quota))


