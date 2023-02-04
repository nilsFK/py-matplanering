#!/usr/bin/env python
# -*- coding: utf-8 -*-
from py_matplanering.utilities.time_helper import (
    parse_date,
    get_date_range,
    time_now,
    format_datetime
)

import copy

class ScheduleEvent:
    def __init__(self, event_dct: dict):
        if not isinstance(event_dct, dict):
            raise Exception('ScheduleEvent may only be instance of dict, instead got: %s' % type(event_dct))
        self.__event = event_dct

    def get_name(self):
        return self.__event['name']

    def get_rules(self):
        return self.__event['rules']

    def set_candidates(self, candidates: list):
        self.__event['candidates'] = candidates

    def get_candidates(self) -> list:
        return self.__event['candidates']

    def as_dict(self):
        return self.__event


class Schedule:
    """
    Schedule is simply organized by:
    each Schedule has many days.
    each day has many ScheduleEvent.
    """
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
        sch_dct = copy.deepcopy(self.schedule)
        for day_num in sch_dct['days']:
            day = sch_dct['days'][day_num]
            tmp_events = []
            for event in day['events']:
                event_dct = copy.deepcopy(event.as_dict())
                if self.sch_options.get('include_props'):
                    new_event_dct = dict((k, event_dct[k]) for k in self.sch_options['include_props'] if k in event_dct)
                tmp_events.append(new_event_dct)
            sch_dct['days'][day_num]['events'] = tmp_events
            del tmp_events
        return sch_dct

    def mark_as_built(self):
        self.schedule['built_dt'] = time_now()

    def get_day(self, date: str):
        return self.schedule['days'][date]

    def get_days(self):
        return self.schedule['days']

    def add_event(self, date: str, sch_event: ScheduleEvent):
        if not isinstance(sch_event, ScheduleEvent):
            raise Exception('Event must be instance of ScheduleEvent, instead got: %s' % (repr(sch_event)))
        selected_day = self.get_day(date)
        if selected_day is None:
            raise Exception("Attempting to add event to missing schedule date: %s" % (date))
        selected_day['events'].append(sch_event)
        if self.sch_options['daily_event_limit']:
            if len(selected_day['events']) > self.sch_options['daily_event_limit']:
                raise Exception('A schedule day is restricted to contain only %s event, exceeded given date %s: %s' % (date, selected_day['events']))

    def get_events(self) -> list:
        days = self.get_days()
        events = []
        for date in days:
            events.extend(days[date]['events'])
        return events
