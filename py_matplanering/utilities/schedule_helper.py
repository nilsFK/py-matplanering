#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Helper methods specifically related to schedules (Schedule) and schedule events (ScheduleEvent).
"""
from __future__ import annotations

from py_matplanering.core.schedule.schedule_input import ScheduleInput
from py_matplanering.core.schedule.schedule import Schedule
from py_matplanering.core.context import BoundaryContext

from py_matplanering.utilities import (common, loader)

from typing import Callable, List

def make_schedule(sch_options: dict):
    return Schedule(sch_options)

def load_boundaries(sch_inp: ScheduleInput) -> dict:
    """ Loads all boundaries as required by the schedule input. """
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

def filter_events_by_date_period(sch: Schedule, date: str, sch_events: List[ScheduleEvent]) -> List[ScheduleEvent]:
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

def run_filter_events_function_chain(sch: Schedule, dates: list, sch_events: List[ScheduleEvent], functions: list) -> List[ScheduleEvent]:
    filtered_sch_events = sch_events
    for date in dates:
        for filter_fn in functions:
            filtered_sch_events = filter_fn(sch, date, filtered_sch_events)
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
