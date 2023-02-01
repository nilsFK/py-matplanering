#!/usr/bin/env python
# -*- coding: utf-8 -*-
from py_matplanering.core.schedule_input import ScheduleInput
from py_matplanering.core.schedule import Schedule

from py_matplanering.utilities import (common, loader)

def make_schedule(sch_options: dict):
    return Schedule(sch_options)

def extract_boundaries(inp: ScheduleInput) -> dict:
    rule_set = inp.get_rule_set()
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
