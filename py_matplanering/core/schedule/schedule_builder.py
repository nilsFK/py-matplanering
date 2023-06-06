#!/usr/bin/env python
# -*- coding: utf-8 -*-

from py_matplanering.core.planner.planner_base import PlannerBase
from py_matplanering.core.schedule.schedule import Schedule, ScheduleEvent
from py_matplanering.core.schedule.schedule_input import ScheduleInput
from py_matplanering.core.schedule.schedule_manager import ScheduleManager
from py_matplanering.core.context import BoundaryContext, ScheduleEventFilterContext
from py_matplanering.core.error import BaseError

from py_matplanering.utilities import (
    schedule_helper,
    time_helper,
    common,
    misc
)
from py_matplanering.utilities.logger import Logger, LoggerLevel

import copy, random

from typing import Any, Union, List, Callable

class ScheduleBuilderError(BaseError):
    def __init__(self, message, capture_data = {}):
        super(ScheduleBuilderError, self).__init__(message)
        self.capture_data = capture_data

    def __str__(self):
        return self.message

class ScheduleBuilder:
    """ ScheduleBuilder is designed to help in the construction
    of a Schedule without going too much in depth with business logic.
    Instead, it supports that process by offering an infrastructure of
    building the different parts needed to assemble a finished Schedule.
    The planning is handled outside of this class, but supported classes
    may use ScheduleBuilder to handle integral decisions to build on.
    ScheduleBuilder internally uses ScheduleManager to separate distinct
    classes of schedules:
        * Master schedule, which is the actual produced Schedule returned by the builder.
        * Minion schedule, which is used to create candidates that are converted
            into actual events within the Master schedule.
    ScheduleBuilder is also able to parse boundaries (Boundary) and planners (Planner).
    An example of a flow of building could look like this:
    sb = ScheduleBuilder()
    sb.set_planner(<planner>)
    schedule = Schedule(...)
    sb.set_schedule(schedule)
    sb.set_build_options(<build options>)
    # def planner():
    sb.plan_logic()
    sb.build()
    schedule = sb.extract_schedule()
    """
    def __init__(self):
        self.__build_status = None
        self.__build_options = dict(
            build_candidates=True,
            apply_boundaries=True,
            planning=dict(
                exclude_event_ids=[]
            )
        )
        self.sch_inp = None
        self.__planner = None
        self.__boundaries = None
        self.__sch_manager = ScheduleManager()
        self.__filter_event_functions = []

    def set_planner(self, planner: PlannerBase):
        """ May only be called once. """
        if planner is None:
            raise ScheduleBuilderError('Planner must be subclass instance of PlannerBase')
        if self.__planner is not None:
            raise ScheduleBuilderError('Planner is already set. May only be set once for each instance of ScheduleBuilder')
        self.__planner = planner
        self.__planner.set_schedule_builder(self)

    def set_schedule(self, schedule: Schedule):
        """ This method should only be called once. Due to setting
            master schedule and spawning candidates from the master
            schedule.
        """
        Logger.log('Setting schedule to: %s' % (schedule), verbosity=LoggerLevel.INFO)
        if schedule is None:
            raise ScheduleBuilderError('Schedule is not allowed to be null')
        if self.__sch_manager.has_master_schedule():
            raise ScheduleBuilderError('Schedule is already set. May only be set once for each instance of ScheduleBuilder')
        self.__sch_manager.add_master_schedule(schedule)
        self.__sch_manager.spawn_minion_schedule('candidates')

    def set_build_options(self, build_options: dict):
        Logger.log('Setting build options to: %s' % (build_options), verbosity=LoggerLevel.DEBUG)
        self.__build_options.update(build_options)

    def get_build_options(self) -> dict:
        return self.__build_options

    def get_schedule_options(self) -> dict:
        return self.__sch_manager.get_master_schedule().get_options()

    def load_boundaries(self) -> dict:
        Logger.log('Loading boundaries', verbosity=LoggerLevel.DEBUG)
        boundaries = schedule_helper.load_boundaries(self.sch_inp)
        Logger.log('Loaded boundaries: %s' % (boundaries), verbosity=LoggerLevel.DEBUG)
        return boundaries

    def set_boundaries(self, boundaries: dict):
        self.__boundaries = boundaries

    def get_boundaries(self) -> dict:
        return self.__boundaries

    def allow_build_candidates(self):
        return self.__build_options['build_candidates'] is True

    def get_candidates(self, as_sorted: bool=False, as_list: bool=False) -> Any:
        candidates = self.__sch_manager.get_minion_schedule('candidates').get_days()
        if as_list:
            if as_sorted:
                return sorted(list(candidates))
            return list(candidates)
        return candidates

    def build_candidates(self, boundaries: dict, match_boundary_cb=None):
        Logger.log(verbosity=LoggerLevel.INFO)
        if self.__build_options['build_candidates'] is False:
            raise ScheduleBuilderError('Unable to build candidates because marked as not allowed')
        event_data = self.sch_inp.get_event_data(require_active=True, event_defaults=self.__sch_manager.get_master_schedule().get_options('event_defaults'))
        all_dates = self.get_candidates(as_sorted=True, as_list=True)
        final_rule_set = schedule_helper.convert_rule_set(self.sch_inp, boundaries)
        Logger.log('Converted final rule set into: %s' % (final_rule_set), LoggerLevel.INFO)
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
                        boundary_context = BoundaryContext(self.__sch_manager, [event], all_dates)
                        date_matches = boundary_obj.filter_eligible_dates(boundary_context)
                        matching_dates = matching_dates.intersection(set(date_matches))
            matching_dates = sorted(list(matching_dates))
            event.set_candidates(matching_dates)
            for date in event.get_candidates():
                self.get_candidates()[date]['events'].append(event)
        return self.get_candidates()

    def build_event_mapping(self, candidates: list, event_mapping: dict):
        """ Maps event id -> event (from candidates) into event_mapping """
        Logger.log('Building event mapping', verbosity=LoggerLevel.INFO)
        for date in candidates:
            for event in candidates[date]['events']:
                if event_mapping.get(event.get_id()):
                    continue
                event_mapping[event.get_id()] = event

    def build_event_occurrence(self, candidates: list, sch_event_dct: dict):
        """ How many times has an event occurred within candidates?
        Such information is placed into sch_event_dct. """
        Logger.log('Building event occurrence from candidates', verbosity=LoggerLevel.INFO)
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
                # TODO: could be removed? or needed for debug info?
                sch_event_dct[event.get_id()]['occurrence'] += 1
                sch_event_dct[event.get_id()]['dates'].append(date)

    def build_quota_iter_plan(self, sch_event_id: int, quota_plan: dict, valid_dates: list) -> list:
        Logger.log('Building quota iteration plan', verbosity=LoggerLevel.INFO)
        sch_startdate = self.__sch_manager.get_master_schedule().get_schedule_startdate()
        sch_enddate = self.__sch_manager.get_master_schedule().get_schedule_enddate()
        misc.make_event_quota(sch_startdate, sch_enddate, quota_plan)
        iter_plans = self.__sch_manager.get_master_schedule().add_quota(sch_event_id, min(valid_dates), max(valid_dates), quota_plan)
        return iter_plans

    def build_indeterminate_boundaries(self, candidates: dict, event_dct: dict):
        Logger.log('Building indeterminate boundaries', verbosity=LoggerLevel.INFO)
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
                        quota = dict(
                            min=min_,
                            max=max_,
                            time_unit=time_unit,
                            type='cap'
                        )
                        event_dct[event.get_id()]['quotas'].append(quota)
        return date_to_event_mapping

    def get_event_dates(self, date_event_mapping: dict, dates: list, event_id: int):
        event_dates = []
        for date in date_event_mapping:
            if date in dates:
                event_ids = list(date_event_mapping[date])
                if len(event_ids) == 1 and event_ids[0] == event_id:
                    event_dates.append(date)
        return event_dates

    def register_filter_event_function(self, filter_fn: Callable, test_run: False=bool):
        """ Registers a filter event function.
        It mainly adds the filter function to the builder.
        test_run: runs the filter function through a test run to ensure that the filter
        function works as intended. May cause AssertionError if it fails.
        """
        if not isinstance(filter_fn, Callable):
            raise ScheduleBuilderError("Attempting to register non callable filter function: %s" % (filter_fn))

        # Validate the parameter signature of the filter_fn.
        param_sign_dct = common.get_parameter_signature(filter_fn)
        if len(param_sign_dct) != 1:
            raise ScheduleBuilderError('Expected filter function `%s` parameter signature to contain one and only one parameter (ctx: ScheduleEventFilterContext). Instead got parameter signature: %s (expected parameter length=1, instead got parameter length=%s)' % (repr(filter_fn), param_sign_dct, len(param_sign_dct)))
        ctx_param = list(param_sign_dct.keys()).pop() # suggested param name is 'ctx' but may be renamed by client
        if param_sign_dct[ctx_param]['type'] != ScheduleEventFilterContext:
            raise ScheduleBuilderError('Expected type of input argument `%s` in filter function `%s` to be: %s. Instead got: %s' % (ctx_param, repr(filter_fn), ScheduleEventFilterContext, param_sign_dct[ctx_param]['type']))

        # Optional test run
        if test_run:
            # Attempt to call filter_fn to make sure it works as intended before registering
            tmp_sch = self.__sch_manager.spawn_minion_schedule('tmp_sch')
            tmp_sch.add_date('9999-12-31')
            ok_events = schedule_helper.run_filter_events_function(tmp_sch, '9999-12-31', [], filter_fn)
            assert isinstance(ok_events, list) and len(ok_events) == 0
            self.__sch_manager.despawn_minion_schedule('tmp_sch')

        # Finally: register event
        self.__filter_event_functions.append(filter_fn)

    def _filter_plannable_events(self, date_list: Union[str, list], sch_events: Union[ScheduleEvent, List[ScheduleEvent]]) -> List[ScheduleEvent]:
        Logger.log('Filter plannable events from date list: %s and schedule events: %s' % (date_list, sch_events), LoggerLevel.DEBUG)
        if not isinstance(date_list, list):
            date_list = [date_list]
        if not isinstance(sch_events, list):
            sch_events = [sch_events]

        if len(self.__filter_event_functions) == 0:
            raise ScheduleBuilderError("Missing filter event functions. Expected: at least one filter function. Call register_filter_event_function() to resolve issue.")
        ok_events = schedule_helper.run_filter_events_function_chain(self.__sch_manager.get_master_schedule(), date_list, sch_events, self.__filter_event_functions)
        return ok_events

    def plan_indeterminate_schedule(self, candidates):
        """ Plans schedule by applying indeterminates.
            This planner method will only plan single events
            as long as the event fulfill conditions:
            1.) The event is conclusively indeterminate.
            2.) The quota of the event has not been exceeded.
            3.) The event is not in conflict with other events
                that also want to be planned on the same date.
            """
        Logger.log('Planning indeterminate schedule', verbosity=LoggerLevel.INFO)
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
            multi_iter_plans = []
            for quota_plan in event_meta_info['quotas']:
                iter_plans = self.build_quota_iter_plan(event_id, quota_plan, event_meta_info['dates'])
                multi_iter_plans.append(iter_plans)
            # Construct a schedule_plan from multi_iter_plans.
            for multi_plan in multi_iter_plans:
                for iter_plan in multi_plan:
                    if len(iter_plan['dates']) == 0:
                        continue
                    event_dates = self.get_event_dates(date_to_event_mapping, iter_plan['dates'], event_id)
                    if len(event_dates) > 0:
                        consumer = common.Consumable(event_dates, consumption_quota=iter_plan['quota'])
                        consumed = consumer.consume(callback=lambda consumables: random.sample(consumables, iter_plan['quota']))
                        # Plan consumed dates
                        schedule_plan.append((consumed, event_mapping[event_id]))
                        if consumer.is_all_consumed():
                            # This event has been consumed.
                            continue
                        # Not all samples were consumed
                        raise NotImplementedError # TODO: handle
        # Iterate through the schedule plan and filter plannable events.
        # Plan those events accordingly.
        planned_days = []
        for date_list, sch_event in schedule_plan:
            ok_events = self._filter_plannable_events(date_list, sch_event)
            if len(ok_events) > 0:
                sch_event = self.__planner.plan_single_event(date_list, sch_event)
                sch_event.add_metadata('method', 'indeterminate', scope='__system')
                self.__sch_manager.add_master_event(date_list, sch_event, remove_from_minions=True)
                planned_days.extend(date_list)
        planned_days = list(set(planned_days))
        self.__build_status = 'indeterminates_planned'

    def plan_determinate_schedule(self, candidates):
        # In previous planning phase we created determinate candidates and
        # planned those according to indeterminate rules.
        # We need to look through determinate candidates to find any unplanned dates.
        # Unplanned dates should be sorted out by the planner.
        # At this point, only plan days with one possible event.
        Logger.log('Planning determinate schedule', verbosity=LoggerLevel.INFO)
        for next_date in sorted(list(candidates)):
            method = 'determinate'
            day_obj = candidates[next_date]
            selected_event = None
            if len(day_obj['events']) == 1:
                method = 'determinate_single'
                ok_events = self._filter_plannable_events(next_date, day_obj['events'])
                if len(ok_events) > 0:
                    selected_event = self.__planner.plan_single_event(next_date, ok_events[0])
            if selected_event:
                if not isinstance(selected_event, ScheduleEvent):
                    raise ScheduleBuilderError('Expected event selected by planner to be instance of ScheduleEvent, instead got: %s' % (selected_event))
                selected_event.add_metadata('method', method, scope='__system')
                self.__sch_manager.add_master_event([next_date], selected_event, remove_from_minions=False)
        self.__build_status = 'plan_ok'

    def plan_resolve_conflicts(self, candidates: dict, iter_order: List[str]):
        # In previous phases we identified indeterminate and determinate candidates
        # and planned. However, conflicts were ignored and are instead handled within
        # this planner method.
        Logger.log('Planning resolve conflicts', verbosity=LoggerLevel.INFO)
        method = 'resolve_conflict'
        for next_date in iter_order:
            Logger.log('Attempting to resolve conflict with date %s' % (next_date), verbosity=LoggerLevel.INFO)
            day_obj = candidates[next_date]
            selected_event = None
            if len(day_obj['events']) > 1:
                ok_events = self._filter_plannable_events(next_date, day_obj['events'])
                if len(ok_events) > 0:
                    selected_event = self.__planner.plan_resolve_conflict(self.__sch_manager.get_master_schedule(), next_date, ok_events)
                    Logger.log('Selected id=%s, name=%s' % (selected_event.get_id(), selected_event.get_name()), verbosity=LoggerLevel.INFO)
                else:
                    Logger.log('No OK events found with date %s' % (next_date), LoggerLevel.DEBUG)
            if selected_event:
                if not isinstance(selected_event, ScheduleEvent):
                    raise ScheduleBuilderError('Expected event selected by planner to be instance of ScheduleEvent, instead got: %s' % (selected_event))
                selected_event.add_metadata('method', 'conflict_resolution', scope='__system')
                self.__sch_manager.add_master_event([next_date], selected_event, remove_from_minions=False)
            else:
                Logger.log('No selected event', verbosity=LoggerLevel.INFO)
        self.__build_status = 'plan_ok'

    def reset(self, build_options: dict={}):
        self.__build_status = None
        self.__build_options.update(build_options)

    def build(self):
        Logger.log('Running build()-method', verbosity=LoggerLevel.INFO)
        if self.__build_status != 'plan_ok':
            raise ScheduleBuilderError('Build must be planned, instead got: %s. Run reset() before build()' % (self.__build_status))
        self.__build_status = 'build_ok'

    def get_schedule_input(self):
        return self.sch_inp

    def set_schedule_input(self, sch_inp: ScheduleInput):
        self.sch_inp = sch_inp

    def extract_schedule(self):
        Logger.log('Extracting schedule', verbosity=LoggerLevel.INFO)
        if self.__build_status != 'build_ok':
            raise ScheduleBuilderError('Attempting to extract schedule from builder with no run state. Call build() before extraction of schedule.')
        return self.__sch_manager.get_master_schedule()

    def get_schedule_events(self):
        return self.__schedule.get_events()
