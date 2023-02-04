#!/usr/bin/env python
# -*- coding: utf-8 -*-
from py_matplanering.core.planner.planner_base import PlannerBase
from py_matplanering.core.schedule_input import ScheduleInput
from py_matplanering.core.schedule import Schedule
from py_matplanering.utilities import schedule_helper
from py_matplanering.utilities.schedule_builder import ScheduleBuilder

import random

from typing import Any

class PlannerFoodMenu(PlannerBase):
    def __init__(self):
        pass

    def plan_init(self, inp: ScheduleInput, sch_options: dict) -> Schedule:
        schedule = schedule_helper.make_schedule(sch_options)
        self.sch_builder = ScheduleBuilder(self, schedule)

        self.sch_builder.build(inp)
        return self.sch_builder.extract_schedule()

    def plan_resolve_conflict(self, date: str, conflicting_events: list) -> Any:
        for event in conflicting_events:
            print("Conflicting event:", event.get_name(), " on date ", date)
        r_event = random.choice(conflicting_events)
        print("Selected:", r_event.get_name())
        return r_event

    def plan_missing_event(self, date: str, day_obj: dict) -> Any:
        print("Missing events on date:", date)
        events = self.sch_builder.get_events()
        r_event = random.choice(events)
        print("Selected:", r_event.get_name())
        return r_event
