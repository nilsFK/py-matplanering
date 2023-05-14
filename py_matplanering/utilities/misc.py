#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
misc.py is common low-level functionality
and should not import anything except for
built in packages and py_matplanering.utilities.
It is an alternative to common.py that is similar
but may contain functions that are heavily correlated with
implementation details of the software.
"""
import copy

from py_matplanering.utilities import (
    time_helper
)

from enum import Enum, unique

@unique
class BuildStrategy(Enum):
    IGNORE_PLACED_DAYS = 0
    REPLACE_PLACED_DAYS = 1

def make_event_quota(startdate: str, enddate: str, quota_template: dict) -> list:
    """
        Builds an event quota in the interval startdate - enddate from quota_template.
        quota_template may contain:
            * used
            * quota
            * min
            * max
            * time_unit
        Returns list of dicts based on quota_template.
        Each dict contains object dates which is a list of str dates.
    """
    base_quota = copy.copy(quota_template)
    if base_quota.get('used') is None:
        base_quota['used'] = 0
    if base_quota.get('quota') is None:
        base_quota['quota'] = (base_quota['max'] - base_quota['min']) + 1
    base_quota['overused'] = False
    # required props
    if any(v is None for v in [
        base_quota.get('min'),
        base_quota.get('max'),
        base_quota.get('time_unit')]):
        raise Exception('Required base quota props must contain values: %s' % (base_quota))
    result = []
    if base_quota['time_unit'] == 'year':
        year_range = time_helper.get_year_range(startdate, enddate)
        startdate_year = int(startdate[:4])
        enddate_year = int(enddate[:4])
        for year in year_range:
            first_day_in_year = "%s-01-01" % (year)
            if startdate_year == year:
                first_day = startdate
            else:
                first_day = first_day_in_year
            last_day_in_year = "%s-12-31" % (year)
            if enddate_year == year:
                last_day = enddate
            else:
                last_day = last_day_in_year
            final_range = time_helper.get_date_range(first_day, last_day)
            new_quota = copy.copy(base_quota)
            new_quota['dates'] = final_range
            result.append(new_quota)
            del first_day
            del last_day
            del final_range
            del first_day_in_year
            del last_day_in_year
    elif base_quota['time_unit'] == 'half_year':
        year_range = time_helper.get_year_range(startdate, enddate)
        startdate_year = int(startdate[:4])
        enddate_year = int(enddate[:4])
        for year in year_range:
            days_in_year = time_helper.get_days_in_year(year)
            first_half = round(days_in_year / 2)-1
            center_day = time_helper.get_nth_day_of_year(year, first_half)

            # Build first range
            first_day_in_year = "%s-01-01" % (year)
            if startdate_year == year:
                first_day = startdate
            else:
                first_day = first_day_in_year
            first_range = time_helper.get_date_range(first_day, center_day)
            new_quota = copy.copy(base_quota)
            new_quota['dates'] = first_range
            result.append(new_quota)
            del first_day
            del first_range
            del first_day_in_year

            # Build second range
            last_day_in_year = "%s-12-31" % (year)
            center_day_plus_one = time_helper.format_date(time_helper.add_days(time_helper.parse_date(center_day), +1))
            if center_day_plus_one > enddate:
                continue
            if enddate_year == year:
                last_day = enddate
            else:
                last_day = last_day_in_year
            second_range = time_helper.get_date_range(center_day_plus_one, last_day)
            new_quota = copy.copy(base_quota)
            new_quota['dates']  = second_range
            result.append(new_quota)
            del last_day
            del second_range
            del last_day_in_year

    elif base_quota['time_unit'] == 'month':
        month_range = time_helper.get_monthly_dates(startdate, enddate)
        for start_month in month_range:
            new_quota = copy.copy(base_quota)
            end_month = time_helper.add_months(time_helper.parse_date(start_month), +1)
            end_month = time_helper.format_date(time_helper.add_days(end_month, -1))
            dates_in_range = time_helper.get_date_range(start_month, end_month)
            new_quota['dates'] = dates_in_range
            result.append(new_quota)

    elif base_quota['time_unit'] == 'week':
        week_range = time_helper.get_week_range(startdate, enddate)
        for week_dates in week_range:
            new_quota = copy.copy(base_quota)
            new_quota['dates'] = week_dates
            result.append(new_quota)

    else:
        raise Exception('Provided invalid or unknown quota time unit: %s, given quota: %s' % (base_quota['time_unit'], base_quota))
    return result


