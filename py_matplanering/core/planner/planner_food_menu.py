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

    def plan_resolve_conflict(self, schedule: Schedule, date: str, conflicting_events: list) -> Any:
        ok_events = conflicting_events
        # Step 1: Check if one and only one event has date as candidate. Select that event.
        one_candidate_events = schedule_helper.filter_events(schedule, date, conflicting_events, condition=lambda event: len(event.get_candidates()) == 1)
        if len(one_candidate_events) == 1:
            return one_candidate_events.pop()

        unsorted = []
        for event in conflicting_events:
            planned = len(schedule.get_events_by_id(event.get_id()))
            unsorted.append(dict(planned=planned, event=event, prio=event.get_prio()))
        def select_event(select_by: str, reverse: bool=False):
            sorted_by = sorted(unsorted, key=lambda item: item[select_by], reverse=reverse)
            first_row = sorted_by[0]
            has_diff = True
            for cur_row in sorted_by:
                if cur_row['event'].get_id() == first_row['event'].get_id():
                    continue
                if cur_row[select_by] == first_row[select_by]:
                    has_diff = False
                    break
            if has_diff:
                for row in conflicting_events:
                    if row.get_id() == first_row['event'].get_id():
                        return row
            return None
        # Step 2: Check which event is the least planned. Select that event.
        selected_event = select_event('planned', reverse=False) # lowest planned first
        if selected_event:
            selected_event.add_metadata('method', 'planned_len')
            return selected_event
        # Step 3: If no such events: check which event has the highest prio. Select that event.
        selected_event = select_event('prio', reverse=True) # highest first
        if selected_event:
            selected_event.add_metadata('method', 'prio_len')
            return selected_event
        # Step 4: Last resort. select a random event
        r_event = random.choice(conflicting_events)
        return r_event

    def plan_missing_event(self, schedule, Schedule, date: str, day_obj: dict) -> Any:
        # print("Missing events on date:", date)
        events = self._sch_builder.get_schedule_events()
        r_event = random.choice(events)
        return r_event
