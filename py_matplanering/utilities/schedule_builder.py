#!/usr/bin/env python
# -*- coding: utf-8 -*-

from py_matplanering.core.planner.planner_base import PlannerBase
from py_matplanering.core.schedule import Schedule, ScheduleEvent
from py_matplanering.core.schedule_input import ScheduleInput

from py_matplanering.utilities import schedule_helper

import copy

class ScheduleBuilder:
    def __init__(self, planner: PlannerBase, schedule: Schedule):
        self.__schedule = schedule
        self.__build_status = None
        self.__planner = planner
        self.__inp = None
        self.__build_options = dict(
            build_candidates=True
        )
        self.__candidates = copy.deepcopy(self.__schedule.get_days())

    def extract_boundaries(self) -> dict:
        return schedule_helper.extract_boundaries(self.__inp)

    def get_input(self):
        return self.__inp

    def build_candidates(self, boundaries: dict):
        event_data = self.__inp.get_event_data()
        all_dates = sorted(list(self.__candidates))
        all_dates_set = set(all_dates)
        final_rule_set = schedule_helper.convert_rule_set(self.__inp, boundaries)
        matching_dates = set()
        for event in event_data:
            for event_rule in event.get_rules():
                for apply_rule in final_rule_set[event_rule]['rules']:
                    # TODO: cache boundary object
                    # Applies boundary on event.
                    apply_boundary = {}
                    apply_boundary[apply_rule['boundary']] = apply_rule[apply_rule['boundary']]
                    boundary_obj = apply_rule['boundary_cls']()
                    boundary_obj.set_boundary(apply_boundary)
                    date_matches = boundary_obj.match_event(event, all_dates)
                    matching_dates = all_dates_set & set(date_matches)
            matching_dates = sorted(list(matching_dates))
            event.set_candidates(matching_dates)
            for date in event.get_candidates():
                self.__candidates[date]['events'].append(event)

    def __plan_schedule(self):
        for next_date in sorted(list(self.__candidates)):
            day_obj = self.__candidates[next_date]
            if len(day_obj['events']) == 0:
                print("Planning empty candidate events")
                selected_event = self.__planner.plan_missing_event(next_date, day_obj)
            elif len(day_obj['events']) == 1:
                print("Planning single candidate event")
                selected_event = self.__planner.plan_single_event(next_date, day_obj['events'][0])
            elif len(day_obj['events']) > 1:
                print("Planning multiple candidate events")
                selected_event = self.__planner.plan_resolve_conflict(next_date, day_obj['events'])

            if selected_event:
                if not isinstance(selected_event, ScheduleEvent):
                    raise Exception('Expected event selected by planner to be instance of ScheduleEvent, instead got: %s' % (selected_event))
                self.__schedule.add_event(next_date, selected_event)

    def build(self, inp: ScheduleInput, build_options: dict={}):
        self.__build_status = 'ongoing'
        self.__inp = inp
        self.__build_options.update(build_options)

        if self.__build_options['build_candidates']:
            boundaries = self.extract_boundaries()
            # place out days from event data into schedule as candidates
            self.build_candidates(boundaries)

        self.__plan_schedule()
        return

    def extract_schedule(self):
        if self.__build_status is None:
            raise Exception('Attempting to extract schedule from builder with no run state. Call build() before extraction of schedule.')
        return self.__schedule

    def get_events(self):
        return self.__schedule.get_events()
