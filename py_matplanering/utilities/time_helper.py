#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
time_helper.py is common low-level functionality
and should not import anything except for
built in packages.
"""
import ntpath
import time, datetime

def format_time_struct(time_struct, format='%Y-%m-%d'):
    return time.strftime(format, time_struct)

def format_date(date, format='%Y-%m-%d'):
    return date.strftime(format)

def format_datetime(datetime, format_='%Y-%m-%d %H:%M:%S'):
    return datetime.strftime(format_)

def is_time_struct(data):
    return isinstance(data, time.struct_time)

def is_date(data):
    return isinstance(data, datetime.date)

def is_datetime(data):
    return isinstance(data, datetime.datetime)

def time_now(format_="%Y-%m-%d %H:%M:%S"):
    return time.strftime(format_)
