#!/usr/bin/env python
# -*- coding: utf-8 -*-
from py_matplanering.core.planner.planner_base import PlannerBase
from py_matplanering.core.schedule_input import ScheduleInput
from py_matplanering.core.schedule import Schedule
from py_matplanering.utilities import schedule_helper

import random

class PlannerRandomizer(PlannerBase):
    def __init__(self):
        pass

    def plan_init(self, inp: ScheduleInput, sch_options: dict) -> Schedule:
        schedule = schedule_helper.make_schedule(sch_options)
        self.sch_builder = schedule_helper.ScheduleBuilder(self, schedule)

        self.sch_builder.build(inp, dict(
            build_candidates=False # ignore candidates since events are randomized
        ))
        return self.sch_builder.extract_schedule()

    def plan_resolve_conflict(self, conflicts: list):
        raise Exception('conflicts within PlannerRandomizer should not be able to occur')

    def plan_missing_event(self, date: str, day_obj: dict):
        events = self.sch_builder.get_input().get_event_data()['data']
        r_event = random.choice(events)
        return r_event
