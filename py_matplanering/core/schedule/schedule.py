#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from __future__ import annotations

from py_matplanering.utilities.time_helper import (
    parse_date,
    get_date_range,
    time_now,
    format_datetime
)

import copy

from typing import Any

# ScheduleEvent needs to be in schedule.py to avoid some import issues.
class ScheduleEvent:
    def __init__(self, event_dct: dict):
        if not isinstance(event_dct, dict):
            raise Exception('ScheduleEvent may only be instance of dict, instead got: %s' % type(event_dct))
        self.__event = event_dct
        self.__boundaries = []
        self.__quota = None
        self.__meta = {}

    def get_name(self):
        return self.__event['name']

    def get_id(self):
        return self.__event['id']

    def get_rules(self):
        return self.__event['rules']

    def set_candidates(self, candidates: list):
        self.__event['candidates'] = candidates

    def get_candidates(self) -> list:
        return self.__event['candidates']

    def add_boundary(self, boundary: Any):
        from py_matplanering.core.boundary.boundary_base import BoundaryBase
        if not isinstance(boundary, BoundaryBase):
            raise Exception('Boundary should be instance of BoundaryBase, instead got: %s of type %s' % (boundary, type(boundary)))
        self.__boundaries.append(boundary)

    def get_boundaries(self) -> list:
        return self.__boundaries

    def set_quota(self, quota: int):
        self.__quota = quota

    def get_quota(self) -> int:
        return self.__quota

    def set_metadata(self, key: str, value: Any):
        self.__meta[key] = value

    def get_metadata(self, key: str=None) -> Any:
        if key is None:
            return self.__meta
        return self.__meta[key]

    def as_dict(self):
        return self.__event


class Schedule:
    """
    Schedule is organized by:
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

    def get_startdate(self) -> str:
        return self.schedule['startdate']

    def get_enddate(self) -> str:
        return self.schedule['enddate']

    def get_events_by_date(self, date: str) -> list:
        day = self.get_day(date)
        return day['events']

    def get_events_by_day(self, day) -> list:
        return day['events']

    def day_has_event(self, date: str) -> bool:
        day = self.get_day(date)
        return len(day['events']) > 0

    def add_event(self, dates: list, sch_event: ScheduleEvent):
        """ Adds schedule event to one or more dates. """
        if not isinstance(sch_event, ScheduleEvent):
            raise Exception('sch_event must be instance of ScheduleEvent, instead got: %s of type %s' % (repr(sch_event), type(sch_event)))
        if not isinstance(dates, list):
            raise Exception('dates must be instance of list, instead got: %s of type %s' % (repr(dates), type(dates)))
        for date in dates:
            selected_day = self.get_day(date)
            if selected_day is None:
                raise Exception("Attempting to add event to missing schedule date: %s" % (date))
            selected_day['events'].append(sch_event)
            # TODO: Daily event limit check should be moved to conflict handler
            # if self.sch_options['daily_event_limit']:
            #     if len(selected_day['events']) > self.sch_options['daily_event_limit']:
            #         raise Exception('A schedule day is restricted to contain only %s event, exceeded given date %s: %s' % (date, selected_day['events']))
            #
    def remove_event(self, sch_event: ScheduleEvent):
        for date in self.get_days():
            tmp_events = []
            for event in self.get_events_by_date(date):
                if event.get_id() == sch_event.get_id():
                    continue
                tmp_events.append(event)
            self.get_day(date)['events'] = tmp_events

    def get_events(self) -> list:
        days = self.get_days()
        events = []
        for date in days:
            events.extend(days[date]['events'])
        return events
