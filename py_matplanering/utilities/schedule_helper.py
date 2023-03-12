#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Helper methods specifically related to schedules (Schedule) and schedule events (ScheduleEvent).
"""
from __future__ import annotations

from py_matplanering.core.schedule.schedule_input import ScheduleInput
from py_matplanering.core.schedule.schedule import Schedule

from py_matplanering.utilities import (common, loader)

def make_schedule(sch_options: dict):
    return Schedule(sch_options)

def load_boundaries(sch_inp: ScheduleInput) -> dict:
    """ Loads all boundaries as required by the schedule input. """
    rule_set = sch_inp.get_rule_set()
    boundaries = {}
    for rule_set in rule_set['rule_set']:
        for rule in rule_set['rules']:
            if rule['type'] == 'boundary':
                boundary_module_name = 'boundary_%s' % (rule['boundary'])
                if boundary_module_name not in boundaries:
                    boundaries[boundary_module_name] = None
    boundary_modules = loader.load_boundaries(list(boundaries))
    for boundary in list(boundaries):
        boundaries[boundary] = boundary_modules[boundary]
    return boundaries

def convert_rule_set(inp: ScheduleInput, boundaries: dict) -> dict:
    rule_set_rs = {}
    for rule_set in inp.get_rule_set()['rule_set']:
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
            print("boundary class of %s is %s" % (boundary_obj, boundary_obj.get_boundary_class()))
            if boundary_obj.get_boundary_class() == apply_filters['boundary_class']:
                filtered_boundaries[boundary_key] = boundary_obj
    return filtered_boundaries

def filter_events_by_quota(sch: Schedule, date: str, sch_events: list) -> list:
    filtered_sch_events = []
    for event in sch_events:
        ok, *_ = sch.validate_quota(event, date)
        if ok:
            filtered_sch_events.append(event)
    return filtered_sch_events

