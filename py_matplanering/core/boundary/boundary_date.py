#!/usr/bin/env python
# -*- coding: utf-8 -*-
from py_matplanering.core.boundary.boundary_base import BoundaryBase, BoundaryError
from py_matplanering.core.schedule.schedule import ScheduleEvent
from py_matplanering.core.context import BoundaryContext
from py_matplanering.utilities import time_helper

from typing import List

class BoundaryDate(BoundaryBase):
    def filter_eligible_dates(self, boundary_context: BoundaryContext) -> List[str]:
        ret_dates = []
        for outer_row in self._boundary['date']:
            if isinstance(outer_row, str) and outer_row == 'values':
                iter_outer_row = self._boundary['date']['values']
            elif isinstance(outer_row, dict):
                iter_outer_row = outer_row['values']
            else:
                raise BoundaryError('Unexpected value provided to boundary: %s (value=%s of type=%s). Expected: str=\'values\' or dict' % (self._boundary, outer_row, type(outer_row)))
            for inner_row in iter_outer_row:
                cur_year = time_helper.get_year()
                date_str = "%s-%s-%s" % (cur_year, inner_row['month_number'], inner_row['day_of_month'])
                # validates date_str
                date = time_helper.format_date(time_helper.parse_date(date_str))
                ret_dates.append(date)
        return ret_dates

    def get_boundary_class(self) -> str:
        return 'determinate'
