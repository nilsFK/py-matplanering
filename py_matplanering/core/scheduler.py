#!/usr/bin/env python
# -*- coding: utf-8 -*-
from py_matplanering.core.schedule_input import ScheduleInput
from py_matplanering.core.planner.planner_base import PlannerBase
from py_matplanering.utilities import time_helper

class Scheduler:
    def __init__(self, planner: PlannerBase, sch_options: dict):
        self.__planner = planner
        self.__options = sch_options

    def create_schedule(self, inp: ScheduleInput):
        schedule = self.__planner.plan_init(inp, self.__options)
        schedule.mark_as_built()
        return schedule
