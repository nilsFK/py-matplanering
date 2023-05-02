#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from __future__ import annotations

from py_matplanering.core.error import BaseError

from py_matplanering.utilities.time_helper import (
    parse_date,
    get_date_range,
    time_now,
    format_datetime
)

from py_matplanering.utilities import common, misc, time_helper

import copy, random

from typing import Any, Union, List

class ScheduleError(BaseError):
    def __init__(self, message, capture_data = {}):
        super(ScheduleError, self).__init__(message)
        self.capture_data = capture_data

    def __str__(self):
        return self.message

# ScheduleEvent needs to be in schedule.py to avoid some import issues.
class ScheduleEvent:
    def __init__(self, event_dct: dict):
        if not isinstance(event_dct, dict):
            raise ScheduleError('ScheduleEvent may only be instance of dict, instead got: %s' % type(event_dct))
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

    def get_startdate(self) -> str:
        return self.__event.get('startdate')

    def get_enddate(self) -> str:
        return self.__event.get('enddate')

    def add_boundary(self, boundary: Any):
        from py_matplanering.core.boundary.boundary_base import BoundaryBase
        if not isinstance(boundary, BoundaryBase):
            raise ScheduleError('Boundary should be instance of BoundaryBase, instead got: %s of type %s' % (boundary, type(boundary)))
        self.__boundaries.append(boundary)

    def get_boundaries(self) -> list:
        return self.__boundaries

    def add_metadata(self, key: str, value: Any):
        if key not in self.__meta:
            self.__meta[key] = set()
        self.__meta[key].add(value)

    def get_metadata(self, key: str=None, default=None) -> Any:
        if key is None:
            return self.__meta
        if key in self.__meta:
            return self.__meta[key]
        return [default]

    def as_dict(self, short: bool=False):
        dct = copy.deepcopy(self.__event)
        if dct.get('candidates'):
            showlen = 3
            if len(dct['candidates']) > (showlen*2):
                # TODO: check if candidates is sequential
                partial1 = dct['candidates'][0:showlen]
                partial2 = dct['candidates'][-showlen:]
                interm = ["[...]"]
                dct['candidates'] = partial1 + interm + partial2
        return dct

    def get_prio(self) -> int:
        return self.__event['prio']


class ScheduleQuota:
    def __init__(self):
        self.event_quotas = dict()

    def add_quota(self, event_id: int, startdate: str, enddate: str, quota: dict) -> list:
        event_quota = misc.make_event_quota(startdate, enddate, quota)
        if event_id not in self.event_quotas:
            self.event_quotas[event_id] = []
        self.event_quotas[event_id].extend(event_quota)
        return event_quota

    def __consume_quota_usage(self, sch_event: ScheduleEvent, dates: list, consume: int, dry_run: bool=False) -> list:
        if self.event_quotas.get(sch_event.get_id()) is None:
            # ok, nothing to consume
            return []
        if len(dates) > 1:
            raise NotImplementedError # not handled at this moment
        ret = []
        for quota in self.get(sch_event.get_id()):
            if dry_run:
                quota = copy.copy(quota)
            overlaps = set(dates).intersection(quota['dates'])
            if len(overlaps) > 0:
                quota['used'] += consume
                quota['quota'] -= consume
                quota['quota'] = max(0, quota['quota'])
            ret.append(quota)
        return ret

    def consume_quota_usage(self, sch_event: ScheduleEvent, dates: list, consume: int):
        return self.__consume_quota_usage(sch_event, dates, consume)

    def exists(self, event_id: int) -> bool:
            return self.event_quotas.get(event_id) is not None

    def get(self, event_id: int=None) -> Union[dict, list]:
        if event_id is None:
            return self.event_quotas
        if self.event_quotas.get(event_id) is None:
            return []
        return self.event_quotas[event_id]

    def validate(self, sch_event: ScheduleEvent, dates: list):
        quotas = self.__consume_quota_usage(sch_event, dates, consume=1, dry_run=True)
        for quota in quotas:
            if quota['used'] > quota['max']-quota['min']+1:
                return (False, 'excessive_quota', dict(
                    excessive_quota=quota
                ))
        return(True, 'ok', None)


class Schedule:
    """
    Schedule is organized by:
        each Schedule has many days.
        each day has many ScheduleEvent.
    """
    def __init__(self, sch_options: dict, prep_events: dict={}):
        # self.schedule contains any details that should be
        # visible outside the class via as_dict.
        self.schedule = dict(
            built_dt=False,
            startdate=sch_options['startdate'],
            enddate=sch_options['enddate'],
            days={},
            use_validation=bool(sch_options.get('use_validation', True)),
            event_defaults=sch_options.get('event_defaults', {}),
            name=sch_options.get('name')
        )
        dr = get_date_range(sch_options['startdate'], sch_options['enddate'])
        for date in dr:
            # self.schedule['days'][date] = { 'events': [] }
            self.schedule['days'][date] = { 'events': prep_events.get(date, []) }
        self.sch_options = sch_options
        # { sch_event_id: [ { 'quota': ...} ]}
        self.sch_quota = ScheduleQuota()
        # wr = get_week_range(sch_options['startdate'], sch_options['enddate'])
        # self.week_range = wr # Lazy load?

    def set_name(self, name: str):
        self.schedule['name'] = name

    def get_name(self) -> str:
        return self.schedule['name']

    def add_date(self, date: str):
        if date in self.schedule['days']:
            raise ScheduleError('Attempting to add existing date to schedule: %s' % (date))
        self.schedule['days'][date] = {'events': [] }

    def as_dict(self) -> dict:
        sch_dct = copy.deepcopy(self.schedule)
        sch_dct['options'] = self.sch_options
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

    def get_grouped_events(self, sch_event_id: int=None) -> dict:
        rs = {}
        days = self.get_days()
        for date in days:
            if sch_event_id:
                events = [event for event in days[date]['events'] if event.get_id() == sch_event_id]
            else:
                events = days[date]['events']
            rs[date] = events
        return rs

    def get_events_by_id(self, sch_event_id: int) -> list:
        return self.get_events(sch_event_id)

    def day_has_event(self, date: str) -> bool:
        day = self.get_day(date)
        return len(day['events']) > 0

    def __validate_add_event(self, sch_event: ScheduleEvent, date: str) -> tuple:
        if not isinstance(sch_event, ScheduleEvent):
            raise ScheduleError('sch_event must be ScheduleEvent, instead got type %s (%s)' % (type(sch_event), sch_event))
        if self.schedule['use_validation'] is False:
            return (True, 'skipped', None)
        ok, msg, data = self.sch_quota.validate(sch_event, [date])
        return ok, msg, data

    def validate_quota(self, sch_event: ScheduleEvent, date: str) -> tuple:
        return self.__validate_add_event(sch_event, date)

    def add_event(self, dates: list, sch_event: ScheduleEvent):
        """ Adds schedule event to one or more dates. """
        # print("Add event to dates:", dates)
        if not isinstance(sch_event, ScheduleEvent):
            raise ScheduleError('sch_event must be instance of ScheduleEvent, instead got: %s of type %s' % (repr(sch_event), type(sch_event)))
        if not isinstance(dates, list):
            raise ScheduleError('dates must be instance of list, instead got: %s of type %s' % (repr(dates), type(dates)))
        for date in dates:
            selected_day = self.get_day(date)
            if selected_day is None:
                raise ScheduleError("Attempting to add event to missing schedule date: %s" % (date))
            # Check if it exceeds quota
            valid, validity_msg, validity_data = self.__validate_add_event(sch_event, date)
            if valid:
                selected_day['events'].append(sch_event)
                if len(selected_day['events']) > self.sch_options['daily_event_limit']:
                    event_str = ""
                    for next_event in selected_day['events']:
                        event_str += str(next_event.as_dict())
                        event_str += ", "
                    event_str = event_str.strip(", ")
                    raise ScheduleError('Date (%s) contains multiple (%s) instances of events (%s). Expected: %s event(s)on this date' % (date, len(selected_day['events']), event_str, self.sch_options['daily_event_limit']))
                self.sch_quota.consume_quota_usage(sch_event, dates, consume=1)
            else:
                # Invalid addition not allowed
                validity_data['excessive_event'] = sch_event.as_dict(short=True)
                raise ScheduleError('Invalid event addition due to: %s (details=%s)' % (validity_msg, validity_data))
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

    def add_quota(self, sch_event_id: int, startdate: str, enddate: str, quota: dict) -> list:
        return self.sch_quota.add_quota(sch_event_id, startdate, enddate, quota)

    def get_quotas(self, sch_event_id: int):
        return self.sch_quota.get(sch_event_id)

    def get_options(self, prop: str=None) -> Any:
        if prop:
            return self.sch_options[prop]
        else:
            return self.sch_options


class ScheduleIterator:
    """
        Iterates through a dict representation of a Schedule.
        The order of iteration depends on the iteration method
        provided (iter_method) to the constructor. The order of
        iteration is important to either eliminate repeating patterns
        or accept that repeating patterns will occur to some degree.
        The iteration method produces a list of str dates, e.g.:

        items = { '20xx-01-01': { 'events': [ScheduleEvent(...), ...] }, ..., '20xx-12-31': ... }
        str_date_order = list(ScheduleIterator(items, iter_method='sorted'))
        str_data_order[0] == '20xx-01-01' # True
    """
    def __init__(self, sch_dct: dict, iter_method: str):
        """
            Iterator method (iter_method) may be any of:
                * sorted:   alphabetically sorted order. may cause repeatable patterns
                            of schedule events.
                * random:   randomly generated list. prevents repeatable patterns of
                            schedule events to some degree. should be combined with
                            certain boundaries to fully eliminate repeatable patterns.
        """
        if isinstance(sch_dct, Schedule):
            sch_dct = sch_dct.as_dict()
        if iter_method in ['sorted', 'standard']:
            self.iter_list = sorted(list(sch_dct))
        elif iter_method == 'random':
            iter_list = list(sch_dct)
            random.shuffle(iter_list)
            self.iter_list = iter_list
        else:
            raise ScheduleError('Unknown iteration method: %s. Select from: sorted, random' % (iter_method))
        self.index = 0
        return None

    def __iter__(self):
        return self

    def __next__(self):
        if self.index+1 > len(self.iter_list):
            raise StopIteration
        item = self.iter_list[self.index]
        self.index += 1
        return item
