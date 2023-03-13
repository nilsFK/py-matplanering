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
import copy

from py_matplanering.utilities import (
    time_helper
)

def make_event_quota(startdate: str, enddate: str, quota_template: dict) -> list:
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
    if base_quota['time_unit'] == 'month':
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
        raise Exception('Invalid or unknown quota time unit: %s given quota: %s' % (base_quota['time_unit'], base_quota))
    return result


