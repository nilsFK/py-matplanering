#!/usr/bin/env python
# -*- coding: utf-8 -*-

from py_matplanering.core.planner.planner_base import PlannerBase
from py_matplanering.core.schedule.schedule import Schedule, ScheduleEvent
from py_matplanering.core.schedule.schedule_input import ScheduleInput
from py_matplanering.core.schedule.schedule_manager import ScheduleManager

from py_matplanering.utilities import schedule_helper, time_helper, common

import copy, random

from typing import Any

class ScheduleBuilder:
    def __init__(self):
        self.__build_status = None
        self.__build_options = dict(
            build_candidates=True,
            apply_boundaries=True
        )
        self.sch_inp = None
        self.__planner = None
        self.__boundaries = None
        self.__sch_manager = ScheduleManager()

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
        if self.__sch_manager.has_master_schedule():
            raise Exception('Schedule is already set. May only be set once for each instance of ScheduleBuilder')
        self.__sch_manager.add_master_schedule(schedule)
        self.__sch_manager.spawn_minion_schedule('candidates')

    def set_build_options(self, build_options: dict):
        self.__build_options.update(build_options)

    def get_build_options(self) -> dict:
        return self.__build_options

    def load_boundaries(self) -> dict:
        return schedule_helper.load_boundaries(self.sch_inp)

    def set_boundaries(self, boundaries: dict):
        self.__boundaries = boundaries

    def get_boundaries(self) -> dict:
        return self.__boundaries

    def allow_build_candidates(self):
        return self.__build_options['build_candidates'] is True

    def get_candidates(self, as_list: bool=False, as_sorted: bool=False) -> Any:
        candidates = self.__sch_manager.get_minion_schedule('candidates').get_days()
        if as_list:
            if as_sorted:
                return sorted(list(candidates))
            return list(candidates)
        return candidates

    def build_candidates(self, boundaries: dict, match_boundary_cb=None):
        if self.__build_options['build_candidates'] is False:
            raise Exception('Unable to build candidates because marked as not allowed')
        event_data = self.sch_inp.get_event_data(require_active=True)
        all_dates = self.get_candidates(as_list=True, as_sorted=True)
        final_rule_set = schedule_helper.convert_rule_set(self.sch_inp, boundaries)
        # Narrow down matching event <-> date by applying date intersection by each boundary
        for event in event_data:
            matching_dates = set(all_dates)
            if self.__build_options['apply_boundaries'] is True:
                for event_rule in event.get_rules():
                    for apply_rule in final_rule_set[event_rule]['rules']:
                        # TODO: cache boundary object
                        # Applies boundary on event.
                        # Create boundary object instance and match event against all dates.
                        apply_boundary = {}
                        apply_boundary[apply_rule['boundary']] = apply_rule[apply_rule['boundary']]
                        boundary_obj = apply_rule['boundary_cls']()
                        boundary_obj.set_boundary(apply_boundary)
                        event.add_boundary(boundary_obj)
                        if match_boundary_cb:
                            if not match_boundary_cb(boundary_obj):
                                continue
                        date_matches = boundary_obj.match_event(event, all_dates)
                        matching_dates = matching_dates.intersection(set(date_matches))
            matching_dates = sorted(list(matching_dates))
            event.set_candidates(matching_dates)
            for date in event.get_candidates():
                self.get_candidates()[date]['events'].append(event)
        return self.get_candidates()

    def build_event_mapping(self, candidates: list, event_mapping: dict):
        for date in candidates:
            for event in candidates[date]['events']:
                if event_mapping.get(event.get_id()):
                    continue
                event_mapping[event.get_id()] = event

    def build_event_occurrence(self, candidates: list, sch_event_dct: dict):
        """ How many times has an event occurred within candidates?
        Such information is placed into sch_event_dct. """
        for date in candidates:
            occ_dates = []
            for event in candidates[date]['events']:
                if event.get_id() not in sch_event_dct:
                    sch_event_dct[event.get_id()] = dict(
                        occurrence=0,
                        quotas=[],
                        name=event.get_name(),
                        dates=[]
                    )
                sch_event_dct[event.get_id()]['occurrence'] += 1
                sch_event_dct[event.get_id()]['dates'].append(date)

    def build_quota_iter_plan(self, quota_plan: dict, valid_dates: list):
        quota_plan['planned'] = 0
        quota_plan['quota'] = (quota_plan['max'] - quota_plan['min']) + 1
        quota_plan['iter'] = []
        if quota_plan['time_unit'] == 'month':
            month_range = time_helper.get_monthly_dates(self.__sch_manager.get_master_schedule().get_startdate(), self.__sch_manager.get_master_schedule().get_enddate())
            for start_month in month_range:
                end_month = time_helper.add_months(time_helper.parse_date(start_month), +1)
                end_month = time_helper.format_date(time_helper.add_days(end_month, -1))
                dates_in_range = []
                for date in valid_dates:
                    if date >= start_month and date <= end_month:
                        dates_in_range.append(date)
                quota_plan['iter'].append(dict(
                    start_month=start_month,
                    end_month=end_month,
                    dates=dates_in_range
                ))

    def build_indeterminate_boundaries(self, candidates: dict, event_dct: dict):
        date_to_event_mapping = {}
        processed_ids = set()
        for date in candidates:
            events = candidates[date]['events']
            for event in events:
                if date not in date_to_event_mapping:
                    date_to_event_mapping[date] = set()
                date_to_event_mapping[date].add(event.get_id())
                if event.get_id() in processed_ids:
                    continue
                processed_ids.add(event.get_id())
                found_indeterminates = []
                for boundary in event.get_boundaries():
                    if boundary.get_boundary_class() == 'indeterminate':
                        found_indeterminates.append(boundary)
                if len(found_indeterminates) == 0:
                    continue
                for indeterm_boundary in found_indeterminates:
                    boundary_caps = indeterm_boundary.get_boundary()['cap']
                    for boundary_cap in boundary_caps:
                        min_ = boundary_cap.get('min', 1)
                        max_ = boundary_cap.get('max', min_)
                        time_unit = boundary_cap['time_unit']
                        plan_units = max_ - min_ + 1
                        event_dct[event.get_id()]['quotas'].append(dict(
                            min=min_,
                            max=max_,
                            time_unit=time_unit
                        ))
        return date_to_event_mapping

    def get_event_dates(self, date_event_mapping: dict, dates: list, event_id: int):
        event_dates = []
        for date in date_event_mapping:
            if date in dates:
                event_ids = list(date_event_mapping[date])
                if len(event_ids) == 1 and event_ids[0] == event_id:
                    event_dates.append(date)
        return event_dates

    def plan_indeterminate_schedule(self, candidates):
        """ Plans schedule by applying indeterminates. """
        schedule_plan = []
        boundaries = schedule_helper.convert_boundaries(self.get_boundaries())
        indeterm_boundaries = schedule_helper.filter_boundaries(boundaries, dict(
            boundary_class='indeterminate'
        ))
        event_dct = {}
        self.build_event_occurrence(candidates, event_dct)
        event_mapping = {}
        self.build_event_mapping(candidates, event_mapping)
        date_to_event_mapping = self.build_indeterminate_boundaries(candidates, event_dct)
        for event_id in event_dct:
            event_meta_info = event_dct[event_id]
            iter_plans = []
            for quota_plan in event_meta_info['quotas']:
                self.build_quota_iter_plan(quota_plan, event_meta_info['dates'])
                iter_plans.append(quota_plan)
            for iter_plan in iter_plans:
                for iter_range in iter_plan['iter']:
                    if len(iter_range['dates']) == 0:
                        # Nothing to plan
                        continue
                    # Find all days that only this event occurs in.
                    event_dates = self.get_event_dates(date_to_event_mapping, iter_range['dates'], event_id)
                    # If there are such days, select as many as allowed by {quota}.
                    if len(event_dates) > 0:
                        consumer = common.Consumable(event_dates, consumption_quota=iter_plan['quota'])
                        consumed = consumer.consume(callback=lambda consumables: random.sample(consumables, iter_plan['quota']))
                        # Plan consumed dates
                        schedule_plan.append((consumed, event_mapping[event_id]))
                        if consumer.is_all_consumed():
                            continue

                        raise NotImplementedError
        planned_days = []
        for date_list, sch_event in schedule_plan:
            sch_event = self.__planner.plan_single_event(date_list, sch_event)
            sch_event.set_metadata('method', 'indeterminate')
            self.__sch_manager.add_master_event(date_list, sch_event, remove_from_minions=True)
            planned_days.extend(date_list)
        planned_days = list(set(planned_days))
        self.__build_status = 'indeterminates_planned'

    def plan_determinate_schedule(self, candidates):
        # In previous planning phase we created determinate candidates and
        # planned those according to indeterminate rules.
        # We need to look thru determinate candidates to find any unplanned dates.
        # Unplanned dates should be sorted out by the planner.
        for next_date in sorted(list(candidates)):
            method = 'determinate'
            day_obj = candidates[next_date]
            selected_event = None
            if len(day_obj['events']) == 0:
                method = 'determinate_empty'
            elif len(day_obj['events']) == 1:
                method = 'determinate_single'
                # print("Planning single candidate event")
                selected_event = self.__planner.plan_single_event(next_date, day_obj['events'][0])
            elif len(day_obj['events']) > 1:
                pass
                # print("Conflicting candidate events, resolved later.")
            if selected_event:
                if not isinstance(selected_event, ScheduleEvent):
                    raise Exception('Expected event selected by planner to be instance of ScheduleEvent, instead got: %s' % (selected_event))
                selected_event.set_metadata('method', method)
                self.__sch_manager.add_master_event([next_date], selected_event, remove_from_minions=False)
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
        return self.__sch_manager.get_master_schedule()

    def get_schedule_events(self):
        return self.__schedule.get_events()
