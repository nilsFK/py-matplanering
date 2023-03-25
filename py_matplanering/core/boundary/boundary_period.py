#!/usr/bin/env python
# -*- coding: utf-8 -*-
from py_matplanering.core.boundary.boundary_base import BoundaryBase, BoundaryError
from py_matplanering.core.schedule.schedule import ScheduleEvent
from py_matplanering.core.context import BoundaryContext

from py_matplanering.utilities import time_helper

from typing import List

class BoundaryPeriod(BoundaryBase):
    def filter_eligible_dates(self, boundary_context: BoundaryContext) -> List[str]:
        matching_dates = set()
        period_set = set(self._boundary['period'])
        weekdays = set(time_helper.get_named_weekdays(short=True, to_lower=True))
        quarters = set(['q1', 'q2', 'q3', 'q4'])
        for date in boundary_context.get_dates():
            date_obj = time_helper.parse_date(date)
            for named_value in self._boundary['period']:
                if named_value in weekdays:
                    wd = time_helper.get_weekday_name(date_obj, short=True).lower()
                    if wd in period_set:
                        matching_dates.add(date)
                        continue
                elif named_value in quarters:
                    quarter_num = time_helper.get_quarter(date_obj)
                    quarter_match = "q%s" % (quarter_num)
                    if quarter_match == named_value:
                        matching_dates.add(date)
                        continue
                else:
                    raise BoundaryError('Unknown boundary named rule provided: %s' % (named_value))
        return list(matching_dates)

    def get_boundary_class(self) -> str:
        return 'determinate'
