#!/usr/bin/env python
# -*- coding: utf-8 -*-

from py_matplanering.core.handler.handler import AbstractHandler
from py_matplanering.core.schedule.schedule_request import ScheduleRequest
from py_matplanering.core.schedule.schedule_input import ScheduleInput
from py_matplanering.core.planner.planner_base import PlannerBase

from typing import (Any)

class SetupHandler(AbstractHandler):
    """ Handles initial setup of required objects such as builders and so on.
        (should be first handler) """
    def with_input(self, planner: PlannerBase, sch_inp: ScheduleInput, sch_options: dict={}):
        self.__planner = planner
        self.__sch_inp = sch_inp
        self.__sch_options = sch_options
        return self

    def handle(self, request: Any) -> Any:
        sch_builder = request.get_schedule_builder()
        sch_builder.set_planner(self.__planner)
        sch_builder.set_schedule_input(self.__sch_inp)
        schedule = self.__planner.plan_init(self.__sch_options)
        sch_builder.set_schedule(schedule)
        return super().handle(request)

class DeterminateDecideCandidateHandler(AbstractHandler):
    """ Handles building determinate candidates. """
    def handle(self, request: Any) ->  Any:
        sch_builder = request.get_schedule_builder()
        boundaries = sch_builder.load_boundaries()
        sch_builder.set_boundaries(boundaries)
        if sch_builder.allow_build_candidates():
            def match_boundary_cb(boundary_obj):
                return boundary_obj.get_boundary_class() == 'determinate'
            determ_candidates = sch_builder.build_candidates(boundaries, match_boundary_cb=match_boundary_cb)
            request.set_payload(determ_candidates)
        return super().handle(request)

class IndeterminatePlanningHandler(AbstractHandler):
    """ Handles planning determinate candidates into schedule events. """
    def handle(self, request: Any) ->  Any:
        sch_builder = request.get_schedule_builder()
        determ_candidates = request.get_payload()
        sch_builder.plan_indeterminate_schedule(determ_candidates)
        return super().handle(request)

class DeterminatePlanningHandler(AbstractHandler):
    """ Handles planning determinate candidates """
    def handle(self, request: Any) ->  Any:
        sch_builder = request.get_schedule_builder()
        determ_candidates = request.get_payload()
        sch_builder.plan_determinate_schedule(determ_candidates)
        return super().handle(request)

class ResolveConflictHandler(AbstractHandler):
    """ Resolves any conflicts created by planning handlers. """
    def handle(self, request: Any) ->  Any:
        sch_builder = request.get_schedule_builder()
        # TODO: Resolve conflicts via builder
        return super().handle(request)

class TerminationHandler(AbstractHandler):
    """ Handles terminal actions (should be last handler). """
    def handle(self, request: Any) -> Any:
        sch_builder = request.get_schedule_builder()
        sch_builder.build()
        return None
