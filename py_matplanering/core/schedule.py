#!/usr/bin/env python
# -*- coding: utf-8 -*-
from py_matplanering.utilities.time_helper import (
    parse_date,
    get_date_range,
    time_now,
    format_datetime
)

import copy

class Schedule:
    def __init__(self, sch_options: dict):
        self.schedule = dict(
            default=True,
            built_dt=False,
            startdate=sch_options['startdate'],
            enddate=sch_options['enddate'],
            days={}
        )
        dr = get_date_range(sch_options['startdate'], sch_options['enddate'])
        for date in dr:
            self.schedule['days'][date] = { 'events': [] }
        self.sch_options = sch_options

    def as_dict(self) -> dict:
        return self.schedule

    def mark_as_built(self):
        self.schedule['built_dt'] = time_now()

    def get_day(self, date: str):
        return self.schedule['days'][date]

    def get_days(self):
        return self.schedule['days']

    def add_event(self, date, day, event):
        selected_day = self.get_day(date)
        if selected_day is None:
            raise Exception("Attempting to add event to missing schedule date: %s" % (date))
        new_event = copy.deepcopy(event)
        if self.sch_options.get('include_props'):
            new_event = dict((k, event[k]) for k in self.sch_options['include_props'] if k in new_event)
        selected_day['events'].append(new_event)
        if self.sch_options['daily_event_limit']:
            if len(selected_day['events']) > self.sch_options['daily_event_limit']:
                raise Exception('A schedule day is restricted to contain only %s event, exceeded given date %s: %s' % (date, selected_day['events']))
