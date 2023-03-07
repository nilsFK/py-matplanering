#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from __future__ import annotations

from py_matplanering.utilities.time_helper import (
    parse_date,
    get_date_range,
    time_now,
    format_datetime
)

from py_matplanering.utilities import misc, time_helper

import copy

from typing import Any

# ScheduleEvent needs to be in schedule.py to avoid some import issues.
class ScheduleEvent:
    def __init__(self, event_dct: dict):
        if not isinstance(event_dct, dict):
            raise Exception('ScheduleEvent may only be instance of dict, instead got: %s' % type(event_dct))
        self.__event = event_dct
        self.__boundaries = []
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

    def set_metadata(self, key: str, value: Any):
        self.__meta[key] = value

    def get_metadata(self, key: str=None) -> Any:
        if key is None:
            return self.__meta
        return self.__meta[key]

    def as_dict(self, short: bool=False):
        dct = copy.deepcopy(self.__event)
        if dct.get('candidates'):
            showlen = 3
            if len(dct['candidates']) > (showlen*2):
                # TODO: check if candidates is sequential
                partial1 = dct['candidates'][0:3]
                partial2 = dct['candidates'][-3:]
                interm = ["[...]"]
                dct['candidates'] = partial1 + interm + partial2
        return dct


class Schedule:
    """
    Schedule is organized by:
        each Schedule has many days.
        each day has many ScheduleEvent.
    """
    def __init__(self, sch_options: dict):
        # self.schedule contains any details that should be
        # visible outside the class via as_dict.
        self.schedule = dict(
            default=True,
            built_dt=False,
            startdate=sch_options['startdate'],
            enddate=sch_options['enddate'],
            days={},
            use_validation=bool(sch_options.get('use_validation', True))
        )
        dr = get_date_range(sch_options['startdate'], sch_options['enddate'])
        for date in dr:
            self.schedule['days'][date] = { 'events': [] }
        self.sch_options = sch_options
        # { sch_event_id: [ { 'quota': ...} ]}
        self.event_quotas = {}
        # wr = get_week_range(sch_options['startdate'], sch_options['enddate'])
        # self.week_range = wr # Lazy load?

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

    def get_events_by_week_num(self, week_num: int) -> list:
        events = []
        days = self.get_days()
        for date in days:
            if time_helper.get_week_number(date) == week_num:
                events.extend(days[date]['events'])
        return events

    def get_events(self, sch_event_id: int=None) -> list:
        days = self.get_days()
        events = []
        for date in days:
            if sch_event_id:
                events.extend([event for event in days[date]['events'] if event.get_id() == sch_event_id])
            else:
                events.extend(days[date]['events'])
        return events

    def get_events_by_id(self, sch_event_id: int) -> list:
        return self.get_events(sch_event_id)

    def day_has_event(self, date: str) -> bool:
        day = self.get_day(date)
        return len(day['events']) > 0

    def __consume_quota_usage(self, event_id: int, consume: int):
        if self.event_quotas.get(event_id):
            for quota in self.event_quotas[event_id]:
                quota['used'] += consume
                quota['quota'] -= consume
                quota['quota'] = max(0, quota['quota'])

    def __validate_add_event(self, date: str, event_id: int) -> tuple:
        if self.schedule['use_validation'] is False:
            return (True, 'skipped', None)
        if not isinstance(event_id, int):
            raise Exception('event_id must be int, instead got type %s (%s)' % (type(event_id), event_id))
        if self.event_quotas.get(event_id):
            added_events = self.get_events_by_id(event_id)
            if len(added_events) > 0:
                for quota in self.event_quotas[event_id]:
                    # Check if quota would exceed for sch_event.get_id()
                    if quota['quota'] == 0:
                        return (False, 'quota_exceed', dict(
                            quota=quota,
                            faulty_event_id=event_id,
                            excess=quota['quota']+1
                        ))
                    if quota['type'] == 'cap':
                        if quota['time_unit'] == 'week':
                            # Check if addition of this event would exceed the limit
                            # Find all events with the same week number as current date
                            # Check if it would exceed
                            week_num = time_helper.get_week_number(date)
                            week_events = self.get_events_by_week_num(week_num) # TODO: cache?
                            if len(week_events) > quota['quota']+1:
                                return (False, 'week_quota_exceed', dict(
                                    quota=quota,
                                    week_events=week_events,
                                    excess=len(week_events)-quota['quota']+1
                                ))
                        else:
                            raise Exception('Unhandled validation due to time_unit: %s' % (quota))
                    else:
                        raise Exception("Unhandled validation due to type: %s" % (quota))
        return (True, 'ok', None)

    def validate_quota(self, date: str, sch_event_id: int) -> tuple:
        return self.__validate_add_event(date, sch_event_id)

    def add_event(self, dates: list, sch_event: ScheduleEvent):
        """ Adds schedule event to one or more dates. """
        print("Add event to dates:", dates)
        if not isinstance(sch_event, ScheduleEvent):
            raise Exception('sch_event must be instance of ScheduleEvent, instead got: %s of type %s' % (repr(sch_event), type(sch_event)))
        if not isinstance(dates, list):
            raise Exception('dates must be instance of list, instead got: %s of type %s' % (repr(dates), type(dates)))
        for date in dates:
            selected_day = self.get_day(date)
            if selected_day is None:
                raise Exception("Attempting to add event to missing schedule date: %s" % (date))
            # Check if it exceeds quota
            valid, validity_msg, validity_data = self.__validate_add_event(date, sch_event.get_id())
            if valid:
                selected_day['events'].append(sch_event)
                self.__consume_quota_usage(sch_event.get_id(), consume=1)
            else:
                # Invalid addition not allowed
                validity_data['excessive_event'] = sch_event.as_dict(short=True)
                raise Exception('Invalid event addition due to: %s (details=%s)' % (validity_msg, validity_data))
            # TODO: Daily event limit check should be moved to conflict handler
            # if self.sch_options['daily_event_limit']:
            #     if len(selected_day['events']) > self.sch_options['daily_event_limit']:
            #         raise Exception('A schedule day is restricted to contain only %s event, exceeded given date %s: %s' % (date, selected_day['events']))

    def remove_event(self, sch_event: ScheduleEvent):
        for date in self.get_days():
            tmp_events = []
            for event in self.get_events_by_date(date):
                if event.get_id() == sch_event.get_id():
                    continue
                tmp_events.append(event)
            self.get_day(date)['events'] = tmp_events

    def add_quota(self, sch_event_id: int, quota: dict):
        quota_cpy = copy.deepcopy(quota)
        misc.make_event_quota(quota_cpy)
        if sch_event_id not in self.event_quotas:
            self.event_quotas[sch_event_id] = []
        self.event_quotas[sch_event_id].append(quota_cpy)

    def get_quotas(self, sch_event_id: int):
        if sch_event_id not in self.event_quotas:
            return []
        return self.event_quotas[sch_event_id]
