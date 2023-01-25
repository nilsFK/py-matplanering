#!/usr/bin/env python
# -*- coding: utf-8 -*-
from py_matplanering.core.planner.planner_base import PlannerBase
from py_matplanering.core.input import Input
from py_matplanering.core.schedule import Schedule
from py_matplanering.utilities import schedule_helper

class PlannerRandomizer(PlannerBase):
    def __init__(self):
        pass

    def plan_init(self, inp: Input, options: dict) -> Schedule:
        schedule = schedule_helper.make_schedule(options)
        sb = schedule_helper.ScheduleBuilder(self, schedule)

        sb.build(inp)
        return sb.extract_schedule()

    def plan_schedule(self, schedule: Schedule):
        pass
