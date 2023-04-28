#!/usr/bin/env python
# -*- coding: utf-8 -*-
from py_matplanering.core.planner.planner_base import PlannerBase
from py_matplanering.core.schedule.schedule_input import ScheduleInput
from py_matplanering.core.schedule.schedule import (Schedule, ScheduleEvent)
from py_matplanering.utilities import schedule_helper

import random

from typing import Any

class PlannerRandomizer(PlannerBase):
    def __init__(self):
        pass

    def plan_init(self, sch_options: dict, prep_events: dict={}) -> Schedule:
        schedule = schedule_helper.make_schedule(sch_options, prep_events)
        self._sch_builder.set_build_options(dict(
            apply_boundaries=False # ignore boundaries since events are randomized
        ))
        return schedule

    def plan_resolve_conflict(self, date: str, conflicting_events: list) -> Any:
        """ This should always occur because all events are in conflict since
        no boundaries are ever applied. """
        build_options = self._sch_builder.get_build_options()
        r_event = random.choice(conflicting_events)
        return r_event

    def plan_missing_event(self, date: str, day_obj: dict) -> Any:
        events = self._sch_builder.get_schedule_events()
        r_event = random.choice(events)
        return r_event
