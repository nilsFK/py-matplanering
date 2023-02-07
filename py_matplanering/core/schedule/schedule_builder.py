#!/usr/bin/env python
# -*- coding: utf-8 -*-

from py_matplanering.core.planner.planner_base import PlannerBase
from py_matplanering.core.schedule.schedule import Schedule, ScheduleEvent
from py_matplanering.core.schedule.schedule_input import ScheduleInput

from py_matplanering.utilities import schedule_helper

import copy

class ScheduleBuilder:
    def __init__(self):
        self.__build_status = None
        self.__build_options = dict(
            build_candidates=True,
            apply_boundaries=True
        )
        self.sch_inp = None
        self.__planner = None
        self.__schedule = None

    def set_planner(self, planner: PlannerBase):
        """ May only be called once. """
        if planner is None:
            raise Exception('Planner must be subclass instance of PlannerBase')
        if self.__planner is not None:
            raise Exception('Planner is already set. May only be set once for each instance of ScheduleBuilder')
        self.__planner = planner
        self.__planner.set_schedule_builder(self)

    def set_schedule(self, schedule: Schedule):
        if schedule is None:
            raise Exception('Schedule is not allowed to be null')
        if self.__schedule is not None:
            raise Exception('Schedule is already set. May only be set once for each instance of ScheduleBuilder')
        self.__schedule = schedule
        self.__candidates = copy.deepcopy(self.__schedule.get_days())

    def set_build_options(self, build_options: dict):
        self.__build_options.update(build_options)

    def get_build_options(self) -> dict:
        return self.__build_options

    def extract_boundaries(self) -> dict:
        return schedule_helper.extract_boundaries(self.sch_inp)

    def allow_build_candidates(self):
        return self.__build_options['build_candidates'] is True

    def build_candidates(self, boundaries: dict):
        if self.__build_options['build_candidates'] is False:
            raise Exception('Unable to build candidates because marked as not allowed')
        event_data = self.sch_inp.get_event_data()
        all_dates = sorted(list(self.__candidates))
        all_dates_set = set(all_dates)
        final_rule_set = schedule_helper.convert_rule_set(self.sch_inp, boundaries)
        matching_dates = set()
        for event in event_data:
            if self.__build_options['apply_boundaries'] is True:
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
            else:
                matching_dates = all_dates_set
            matching_dates = sorted(list(matching_dates))
            event.set_candidates(matching_dates)
            for date in event.get_candidates():
                self.__candidates[date]['events'].append(event)

    def plan_schedule(self):
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
        self.__build_status = 'plan_ok'

    def reset(self, build_options: dict={}):
        self.__build_status = None
        self.__build_options.update(build_options)

    def build(self):
        if self.__build_status != 'plan_ok':
            raise Exception('Build must be planned, instead got: %s. Run reset() before build()' % (self.__build_status))
        self.__build_status = 'build_ok'

    def get_schedule_input(self):
        return self.sch_inp

    def set_schedule_input(self, sch_inp: ScheduleInput):
        self.sch_inp = sch_inp

    def extract_schedule(self):
        if self.__build_status != 'build_ok':
            raise Exception('Attempting to extract schedule from builder with no run state. Call build() before extraction of schedule.')
        return self.__schedule

    def get_events(self):
        return self.__schedule.get_events()
