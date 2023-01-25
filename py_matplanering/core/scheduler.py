#!/usr/bin/env python
# -*- coding: utf-8 -*-
from py_matplanering.core.input import Input
from py_matplanering.core.planner.planner_base import PlannerBase
from py_matplanering.utilities import time_helper

class Scheduler:
    def __init__(self, planner: PlannerBase, sch_options: dict):
        self.planner = planner
        self.options = sch_options

    def create_schedule(self, inp: Input):
        schedule = self.planner.plan_init(inp, self.options)
        schedule.set_built()
        return schedule
