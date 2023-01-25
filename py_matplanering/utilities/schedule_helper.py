#!/usr/bin/env python
# -*- coding: utf-8 -*-
from py_matplanering.core.input import Input
from py_matplanering.core.schedule import Schedule
from py_matplanering.core.planner.planner_base import PlannerBase

def make_schedule(sch_options: dict):
    schedule = Schedule(sch_options['startdate'], sch_options['enddate'])
    return schedule

def extract_boundaries(inp: Input):
    pass

def match_ruleset_with(boundaries: list):
    pass

class ScheduleBuilder:
    def __init__(self, planner: PlannerBase, schedule: Schedule):
        self.__schedule = schedule
        self.__build_status = None
        self.__planner = planner

    def build(self, inp: Input):
        self.__build_status = 'ongoing'
        # TODO: do stuff with Input --> Schedule...
        self.__planner.plan_schedule(self.__schedule)
        return

    def extract_schedule(self):
        if self.__build_status is None:
            raise Exception('Attempting to extract schedule from builder with no run state. Call build() before extraction of schedule.')
        return self.__schedule