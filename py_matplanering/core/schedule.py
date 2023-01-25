#!/usr/bin/env python
# -*- coding: utf-8 -*-
from py_matplanering.utilities.time_helper import (
    parse_date,
    get_date_range,
    time_now,
    format_datetime
)

class Schedule:
    def __init__(self, startdate: str, enddate: str):
        self.schedule = dict(
            default=True,
            built=False,
            startdate=startdate,
            enddate=enddate,
            days={}
        )
        md = get_date_range(startdate, enddate)
        default_data = {}
        self.schedule['days'] = dict.fromkeys(md, default_data)

    def as_dict(self) -> dict:
        return self.schedule

    def set_built(self):
        self.schedule['built'] = time_now()