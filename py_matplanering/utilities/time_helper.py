#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
time_helper.py is common low-level functionality
and should not import anything except for
built in packages.
All dates are inclusive.
"""
import ntpath
import time, datetime, math, calendar

from typing import (Any)

def format_time_struct(time_struct, format='%Y-%m-%d'):
    return time.strftime(format, time_struct)

def format_date(date, format_='%Y-%m-%d'):
    return date.strftime(format_)

def format_datetime(datetime, format_='%Y-%m-%d %H:%M:%S'):
    return datetime.strftime(format_)

def parse_datetime(datetime_str, datetime_format='%Y-%m-%d %H:%M:%S'):
    return datetime.datetime.strptime(datetime_str, datetime_format)

def parse_date(date_str, date_format='%Y-%m-%d'):
    return datetime.datetime.strptime(date_str, date_format)

def is_time_struct(data):
    return isinstance(data, time.struct_time)

def is_date(data):
    return isinstance(data, datetime.date)

def is_datetime(data):
    return isinstance(data, datetime.datetime)

def time_now(format_="%Y-%m-%d %H:%M:%S"):
    return time.strftime(format_)

def get_year(d_=None):
    if isinstance(d_, str):
        return d_[:4]
    if d_ is None:
        return time_now("%Y")
    return format_date(d_)[:4]

def month_delta(date, delta):
    m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
    if not m: m = 12
    d = min(date.day, [31,
        29 if y%4==0 and not y%400==0 else 28,31,30,31,30,31,31,30,31,30,31][m-1])
    return date.replace(day=d, month=m, year=y)

def add_months(date, months):
    return month_delta(date, months)

def add_days(date, days):
    return date + datetime.timedelta(days=days)

# Get montly dates between a date interval
# get_monthly_dates("2017-01-01", "2017-12-01") would produce
# 2017-01-01, 2017-02-01, 2017-03-01, ..., 2017-12-01
def get_monthly_dates(start_date: str, end_date: str) -> list:
    dates = []
    next_date = start_date
    while next_date <= end_date:
        dates.append(next_date)
        next_date = format_date(add_months(parse_date(next_date), +1))
    return dates

# Get date range between a date interval
# get_date_range("2017-01-01", "2017-12-01") would produce
# 2017-01-01, 2017-01-02, 2017-01-03, ..., 2017-12-01
def get_date_range(start_date: str, end_date: str) -> list:
    if start_date > end_date:
        raise Exception('start_date=%s exceeds end_date=%s' % (start_date, end_date))
    dates = []
    next_date = start_date
    while next_date <= end_date:
        dates.append(next_date)
        next_date = format_date(add_days(parse_date(next_date), +1))
    return dates

# Gets week range between a date interval
# get_week_range("2017-01-01", "2017-12-01") would produce:
# [ ['2017-01-01'], ['2017-01-02', '2017-01-03', ..., '2017-01-08'], ['2017-01-09', ...] ]
def get_week_range(start_date: str, end_date: str) -> list:
    week_range = []
    cur_date = start_date
    week_buffer = []
    prev_date = None
    while cur_date <= end_date:
        if prev_date and get_week_number(cur_date) != get_week_number(prev_date):
            # new week, clear buffer
            week_range.append(week_buffer)
            week_buffer = []
        week_buffer.append(cur_date)
        prev_date = cur_date
        # last action
        cur_date = format_date(add_days(parse_date(cur_date), +1))
    if len(week_buffer) > 0:
        # adds remaining buffer
        week_range.append(week_buffer)
    return week_range

# Gets year range between a date interval
# get_year_range("2020-01-01", "2023-01-01") would produce list of ints:
# [2020, 2021, 2022, 2023]
def get_year_range(start_date: str, end_date: str) -> list:
    if start_date > end_date:
        raise Exception('start_date=%s exceeds end_date=%s' % (start_date, end_date))
    year_range = []
    start_year = int(start_date[0:4])
    end_year = int(end_date[0:4])
    cur_year = start_year
    while cur_year <= end_year:
        year_range.append(cur_year)
        cur_year += 1
    return year_range

def get_days_in_year(year=datetime.datetime.now().year) -> int:
    return 365 + calendar.isleap(year)

def get_nth_day_of_year(year: int, n: int) -> str:
    if n < 1 or n > 365:
        raise ValueError("n must be between 1 and 365 (inclusive)")
    first_day = datetime.datetime(year, 1, 1)
    nth_day = first_day + datetime.timedelta(days=n-1)
    return nth_day.strftime('%Y-%m-%d')

def get_weekday_name(date: Any, short: bool=False, to_lower: bool=False) -> str:
    if isinstance(date, str):
        date = parse_date(date)
    named_wd = date.strftime('%A')
    if short:
        named_wd = named_wd[:3]
    if to_lower:
        return named_wd.casefold()
    return named_wd

def get_week_number(date: Any) -> int:
    if isinstance(date, str):
        return parse_date(date[0:10]).isocalendar()[1]
    else:
        return date.isocalendar()[1]
    # python 3.9+
    # return parse_date(date).isocalendar().week

def get_named_weekdays(short: bool=False, to_lower: bool=False) -> list:
    nwd = [
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
        'Sunday'
    ]
    if to_lower:
        nwd = [row.casefold() for row in nwd]
    if short:
        nwd = [row[0:3] for row in nwd]
    return nwd

def get_month_name(date: Any, short: bool=False, to_lower: bool=False) -> str:
    if isinstance(date, str):
        date = parse_date(date)
    named_month = date.strftime('%B')
    if short:
        named_month = named_month[:3]
    if to_lower:
        return named_month.casefold()
    return named_month

def get_named_months(short: bool=False, to_lower: bool=False) -> list:
    nm = [
        'January',
        'February',
        'March',
        'April',
        'May',
        'June',
        'July',
        'August',
        'September',
        'October',
        'November',
        'December'
    ]
    assert len(nm) == 12
    if to_lower:
        nm = [row.casefold() for row in nm]
    if short:
        nm = [row[0:3] for row in nm]
    return nm

def get_quarter(date=None):
    """ returns a number between 1-4 representing quarter of date """
    if date is None:
        date = datetime.datetime.now()
    return int(math.ceil(date.month/3.))
