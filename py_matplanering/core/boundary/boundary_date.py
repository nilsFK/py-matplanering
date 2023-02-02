#!/usr/bin/env python
# -*- coding: utf-8 -*-
from py_matplanering.core.boundary.boundary_base import BoundaryBase
from py_matplanering.utilities import time_helper

class BoundaryDate(BoundaryBase):
    def match_event(self, event: dict, dates: list) -> list:
        ret_dates = []
        for outer_row in self.boundary['date']:
            for inner_row in outer_row['values']:
                year = time_helper.get_year()
                date_str = "%s-%s-%s" % (year, inner_row['month_number'], inner_row['day_of_month'])
                # validates date_str
                date = time_helper.format_date(time_helper.parse_date(date_str))
                ret_dates.append(date)
        return ret_dates
