#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Helper methods specifically related to schedules (Schedule) and schedule events (ScheduleEvent).
"""
from __future__ import annotations

from py_matplanering.core.schedule.schedule_input import ScheduleInput
from py_matplanering.core.schedule.schedule import Schedule, ScheduleEvent
from py_matplanering.core.context import BoundaryContext

from py_matplanering.utilities import (common, loader)

from typing import Callable, List

def make_schedule(sch_options: dict, prep_events: dict={}):
    return Schedule(sch_options, prep_events)

def load_boundaries(sch_inp: ScheduleInput) -> dict:
    """ Loads all boundaries as required by the schedule input.
        Raises Exception if an unknown rule type has been provided
        by the schedule input.
    """
    rules = []
    for rule_set_meta in sch_inp.get_rule_set():
        for rule_set in rule_set_meta['rule_set']:
            for rule in rule_set['rules']:
                rule['scope'] = rule_set_meta['scope']
                rules.append(rule)
    boundaries = {}
    for rule in rules:
        if rule['type'] == 'boundary':
            boundary_module_name = 'boundary_%s' % (rule['boundary'])
            if boundary_module_name not in boundaries:
                boundaries[boundary_module_name] = None
        else:
            raise Exception('Unknown rule type provided: %s' % (rule['type']))
    boundary_modules = loader.load_boundaries(list(boundaries))
    for boundary in list(boundaries):
        boundaries[boundary] = boundary_modules[boundary]
    return boundaries

def convert_rule_set(inp: ScheduleInput, boundaries: dict) -> dict:
    rule_set_rs = {}

    for rule_set_meta in inp.get_rule_set():
        for rule_set in rule_set_meta['rule_set']:
            rule_set_rs[rule_set['name']] = {}
            rule_set_rs[rule_set['name']]['id'] = rule_set['id']
            rule_set_rs[rule_set['name']]['rules'] = rule_set['rules']
            for rule in rule_set_rs[rule_set['name']]['rules']:
                if rule['type'] == 'boundary':
                    rule['boundary_module'] = boundaries['boundary_' + rule['boundary']]
                    cls_name = common.underscore_to_camelcase('boundary_' + rule['boundary'])
                    rule['boundary_cls'] = getattr(rule['boundary_module'], cls_name)
    return rule_set_rs

def convert_boundaries(boundaries: dict) -> dict:
    converted_boundaries = {}
    for boundary_key in list(boundaries):
        boundary_module = boundaries[boundary_key]
        cls_name = common.underscore_to_camelcase(boundary_key)
        boundary_cls = getattr(boundary_module, cls_name)
        converted_boundaries[boundary_key] = boundary_cls()
    return converted_boundaries

def filter_boundaries(boundaries: dict, apply_filters: dict={}) -> dict:
    filtered_boundaries = {}
    for boundary_key in list(boundaries):
        boundary_obj = boundaries[boundary_key]
        if apply_filters.get('boundary_class'):
            # print("boundary class of %s is %s" % (boundary_obj, boundary_obj.get_boundary_class()))
            if boundary_obj.get_boundary_class() == apply_filters['boundary_class']:
                filtered_boundaries[boundary_key] = boundary_obj
    return filtered_boundaries

def filter_events_by_planning_range(sch: Schedule, date: str, sch_events: List[ScheduleEvent]) -> List[ScheduleEvent]:
    """ Checks if date is within planning range. If so, return all events.
        Otherwise, return empty list. """
    if date > sch.get_planning_enddate():
        return []
    if date < sch.get_planning_startdate():
        return []
    # date is within planning range, return all events
    return sch_events

def filter_events_by_placing(sch: Schedule, date: str, sch_events: List[ScheduleEvent]) -> List[ScheduleEvent]:
    """ Returns empty list if date has been placed in schedule (sch) """
    placed_events = sch.get_events_by_date(date)
    if len(placed_events) > 0:
        return []
    # date has not been placed in sch, return all events
    return sch_events

def filter_events_by_date_period(sch: Schedule, date: str, sch_events: List[ScheduleEvent]) -> List[ScheduleEvent]:
    """ Events can be restricted to a given period (min, max) where planning is allowed.
        Checks if date is within the event date period restriction. """
    filtered_sch_events = []
    for event in sch_events:
        event_sdate, event_edate = event.get_startdate(), event.get_enddate()
        if event_sdate is None or event_edate is None:
            filtered_sch_events.append(event)
            continue
        if date > event_edate:
            continue
        if date < event_sdate:
            continue
        filtered_sch_events.append(event)
    return filtered_sch_events

def filter_events_by_quota(sch: Schedule, date: str, sch_events: List[ScheduleEvent]) -> List[ScheduleEvent]:
    filtered_sch_events = []
    for event in sch_events:
        ok, *_ = sch.validate_quota(event, date)
        if ok:
            filtered_sch_events.append(event)
    return filtered_sch_events

def filter_events_by_distance(sch: Schedule, date: str, sch_events: List[ScheduleEvent]) -> List[ScheduleEvent]:
    filtered_sch_events = []
    for sch_event in sch_events:
        event_ok = True
        for boundary in sch_event.get_boundaries():
            if boundary.get_boundary_class() == 'distance':
                ok_events = boundary.filter_eligible_events(BoundaryContext(sch, [sch_event], [date]))
                if len(ok_events) == 0:
                    event_ok = False
                    break
        if event_ok:
            filtered_sch_events.append(sch_event)
    return filtered_sch_events

def run_filter_events_function(sch: Schedule, date: str, sch_events: List[ScheduleEvent], filter_fn: Callable) -> List[ScheduleEvent]:
    if not isinstance(sch, Schedule):
        raise Exception('sch is not instance of Schedule, instead got: %s' % (sch))
    filtered_sch_events = filter_fn(sch, date, sch_events)
    if not isinstance(filtered_sch_events, list):
        raise Exception('Applied filter function unexpectedly returned non list: %s' % (filtered_sch_events))
    return filtered_sch_events

def run_filter_events_function_chain(sch: Schedule, dates: list, sch_events: List[ScheduleEvent], functions: list) -> List[ScheduleEvent]:
    filtered_sch_events = sch_events
    for date in dates:
        for filter_fn in functions:
            filtered_sch_events = run_filter_events_function(sch, date, filtered_sch_events, filter_fn)
            if len(filtered_sch_events) == 0:
                return []
    return filtered_sch_events

def filter_events(sch: Schedule, date: str, sch_events: list, condition: Callable[[ScheduleEvent], bool]) -> List[ScheduleEvent]:
    filtered_sch_events = []
    for event in sch_events:
        ok = condition(event)
        if ok:
            filtered_sch_events.append(event)
    return filtered_sch_events

def get_placed_schedule_dates(sch: Schedule) -> List[str]:
    placed_sch_dates = []
    result = sch.get_grouped_events()
    for date in result:
        if len(result[date]) > 0:
            placed_sch_dates.append(date)
    return placed_sch_dates

def count_placed_schedule_days(sch: Schedule) -> int:
    """ Counts how many days in schedule have been "placed", e.g.
        contains at least one event. """
    return len(get_placed_schedule_dates(sch))

def parse_schedule(sch_dct: dict) -> Schedule:
    """ Converts sch_dct into an instance of Schedule
        Also parses any related sub instances to Schedule,
        such as ScheduleEvent.
    """
    schedule = make_schedule(sch_dct['options'])
    for date in schedule.get_days():
        sch_events_list = sch_dct['days'][date]['events']
        for event_dct in sch_events_list:
            sch_event_obj = ScheduleEvent(event_dct)
            # Events should by default not contain any candidates.
            sch_event_obj.set_candidates([])
            schedule.add_event([date], sch_event_obj)
    return schedule

def is_schedule_complete(sch: Schedule) -> bool:
    """ Are all days planned with event(s) in schedule range? """
    for date in sch.get_days():
        events = sch.get_events_by_date(date)
        if len(events) == 0:
            return False
    return True

# TODO: implement if needed
# def merge_schedules(sch1: Schedule, sch2: Schedule, conflict_schema: dict={}):
#     """ Merge sch1 and sch2 into a new schedule.
#         Any duplicate data is overwritten by sch2.
#         So the ordering of sch1 and sch2 is important.
#         If there are conflicts in merge which cannot be resolved,
#         it will be instead be determined from the conflict_schema.
#         This method is not yet capable of handling
#         non-consecutive schedules. Consider the following schedule graph
#         (left to right):

#         |----| (S1)
#                     |----| (S2)

#         Since there is a gap between end of S1 and start of S2,
#         a merge would include that gap period, which
#         is not an expected behavior.
#     """
#     # Create a new Schedule instance
#     new_schedule = Schedule(sch2.get_options())

#     # Resolve any merge conflicts
#     if sch1.use_validation != sch2.use_validation:
#         new_schedule.use_validation = conflict_schema['use_validation']

#     # Overwrite some specific props
#     new_schedule.startdate = min(sch1.startdate, sch2.startdate)
#     new_schedule.enddate = max(sch1.enddate, sch2.enddate)

#     # Combine the days from the two schedules
#     # TODO: this is only partially correct.
#     # 1.) it needs to merge events based on their ids.
#     # 2.) if sch1.event.id == sch2.event.id we're good.
#     # 3.) if sch1.event.id != sch2.event.id there is a conflict. Current fix is to prefer sch2.id and overwrite sch1.id.
#     #       (if only one event allowed per day)
#     # 4.) ???
#     # for date in sch1.schedule['days']:
#     #     if date in sch2.schedule['days']:
#     #         new_schedule.schedule['days'][date] = {
#     #             'events': sch1.schedule['days'][date]['events'] + sch2.schedule['days'][date]['events']
#     #         }
#     #     else:
#     #         new_schedule.schedule['days'][date] = sch1.schedule['days'][date]
#     # for date in sch2.schedule['days']:
#     #     if date not in sch1.schedule['days']:
#     #         new_schedule.schedule['days'][date] = sch2.schedule['days'][date]
#     #
#     # combine the event defaults from the two schedules
#     new_schedule.schedule['event_defaults'] = {
#         **sch1.schedule['event_defaults'],
#         **sch2.schedule['event_defaults']
#     }
#     # combine the quota from the two schedules
#     # TODO: merge quota by inspecting event_quotas...
#     #
#     # new_schedule.sch_quota = sch1.sch_quota + sch2.sch_quota
#     return new_schedule

#     # self.schedule = dict(
#     #     built_dt=False,
#     #     startdate=sch_options['startdate'],
#     #     enddate=sch_options['enddate'],
#     #     days={},
#     #     use_validation=bool(sch_options.get('use_validation', True)),
#     #     event_defaults=sch_options.get('event_defaults', {})
#     # )
