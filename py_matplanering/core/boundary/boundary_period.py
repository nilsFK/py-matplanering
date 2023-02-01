#!/usr/bin/env python
# -*- coding: utf-8 -*-
from py_matplanering.core.boundary.boundary_base import BoundaryBase
from py_matplanering.utilities import time_helper

class BoundaryPeriod(BoundaryBase):
    def match_event(self, event: dict, dates: list) -> bool:
        print("Trying to match event (BoundaryPeriod):", event, "with dates", dates, "against", self.boundary)
        matching_dates = []
        for date in dates:
            wd = time_helper.get_weekday_name(time_helper.parse_date(date), short=True).lower()
            if wd in self.boundary['period']:
                matching_dates.append(date)

        return matching_dates
