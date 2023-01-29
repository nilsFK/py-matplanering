#!/usr/bin/env python
# -*- coding: utf-8 -*-
from py_matplanering.core.schedule_input import ScheduleInput
from py_matplanering.core.schedule import Schedule
from py_matplanering.core.planner.planner_base import PlannerBase

from py_matplanering.utilities import loader

import copy

def make_schedule(sch_options: dict):
    schedule = Schedule(sch_options)
    return schedule

def extract_boundaries(inp: ScheduleInput):
    rule_set = inp.get_rule_set()
    boundaries = {}
    for ruleset in rule_set['ruleset']:
        for rule in ruleset['rules']:
            if rule['type'] == 'boundary':
                boundary_module_name = 'boundary_%s' % (rule['boundary'])
                if boundary_module_name not in boundaries:
                    boundaries[boundary_module_name] = None
    boundary_modules = loader.load_boundaries(list(boundaries))
    for boundary in list(boundaries):
        boundaries[boundary] = boundary_modules[boundary]
    return boundaries

class ScheduleBuilder:
    def __init__(self, planner: PlannerBase, schedule: Schedule):
        self.__schedule = schedule
        self.__build_status = None
        self.__planner = planner
        self.__inp = None
        self.__build_options = dict(
            build_candidates=True
        )
        self.__candidates = copy.deepcopy(self.__schedule.get_days())

    def extract_boundaries(self):
        return extract_boundaries(self.__inp)

    def get_input(self):
        return self.__inp

    def build_candidates(self, boundaries: list):
        tagged_data = self.__inp.get_tagged_data()
        # TODO: Build candidates...
        # * Iterate tagged data rows
        # * Apply boundary on tagged data row
        # * Determine which days tagged data row is candidate for.
        # * Place out tagged data row in schedule
        #   and mark tagged data row as candidate

    def __plan_schedule(self):
        for next_date in sorted(list(self.__candidates)):
            day_obj = self.__candidates[next_date]
            if len(day_obj['events']) == 0:
                selected_event = self.__planner.plan_missing_event(next_date, day_obj)
            elif len(day_obj['events']) == 1:
                selected_event = day_obj['events'][0]
            elif len(day_obj['events']) > 1:
                selected_event = self.__planner.plan_resolve_conflict(day_obj['events'])

            if selected_event:
                self.__schedule.add_event(next_date, day_obj, selected_event)

    def build(self, inp: ScheduleInput, build_options: dict={}):
        self.__build_status = 'ongoing'
        self.__inp = inp
        self.__build_options.update(build_options)

        if self.__build_options['build_candidates']:
            boundaries = self.extract_boundaries()
            # place out days from tagged data into schedule as candidates
            self.build_candidates(boundaries)

        self.__plan_schedule()
        return

    def extract_schedule(self):
        if self.__build_status is None:
            raise Exception('Attempting to extract schedule from builder with no run state. Call build() before extraction of schedule.')
        return self.__schedule
