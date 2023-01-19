#!/usr/bin/env python
# -*- coding: utf-8 -*-
from py_matplanering.core.input import Input
from py_matplanering.core.planner.planner_base import PlannerBase
from py_matplanering.core.planner.planner_eugene import PlannerEugene
from py_matplanering.core.planner.planner_randomizer import PlannerRandomizer

class Scheduler:
    def __init__(self, planner: PlannerBase):
        self.planner = planner

    def create_schedule(self, inp: Input):
        schedule = self.planner.plan(inp)
        return schedule
