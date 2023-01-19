#!/usr/bin/env python
# -*- coding: utf-8 -*-
from py_matplanering.core.planner.planner_base import PlannerBase
from py_matplanering.core.input import Input
from py_matplanering.core.schedule import Schedule

class PlannerRandomizer(PlannerBase):
    def __init__(self):
        pass # TODO: call super

    def plan(self, inp: Input) -> Schedule:
        schedule = Schedule()
        # TODO: Randomize input...
        return schedule

