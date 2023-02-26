#!/usr/bin/env python
# -*- coding: utf-8 -*-
from py_matplanering.core.planner.planner_base import PlannerBase
from py_matplanering.core.schedule.schedule_input import ScheduleInput
from py_matplanering.core.schedule.schedule import Schedule
from py_matplanering.utilities import schedule_helper

import random

from typing import Any

class PlannerFoodMenu(PlannerBase):
    def plan_init(self, sch_options: dict) -> Schedule:
        # Current version only allows one event each day.
        # TODO: Add multi event support.
        sch_options['daily_event_limit'] = 1
        schedule = schedule_helper.make_schedule(sch_options)
        return schedule

    def plan_resolve_conflict(self, date: str, conflicting_events: list) -> Any:
        for event in conflicting_events:
            print("Conflicting event:", event.get_name(), " on date ", date)
        r_event = random.choice(conflicting_events)
        print("Selected:", r_event.get_name())
        return r_event

    def plan_missing_event(self, date: str, day_obj: dict) -> Any:
        print("Missing events on date:", date)
        events = self._sch_builder.get_schedule_events()
        r_event = random.choice(events)
        print("Selected:", r_event.get_name())
        return r_event
