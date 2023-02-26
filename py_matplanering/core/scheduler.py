#!/usr/bin/env python
# -*- coding: utf-8 -*-
from py_matplanering.core.schedule.schedule_input import ScheduleInput
from py_matplanering.core.schedule.schedule_request import ScheduleRequest
from py_matplanering.core.schedule.schedule_builder import ScheduleBuilder
from py_matplanering.core.planner.planner_base import PlannerBase
from py_matplanering.core.handler.handler_impl import (
    SetupHandler,
    DeterminateDecideCandidateHandler,
    IndeterminatePlanningHandler,
    DeterminatePlanningHandler,
    ResolveConflictHandler,
    TerminationHandler
)
from py_matplanering.core.handler.handler_helper import (
    link_handler_chain,
    run_handler_chain
)
from py_matplanering.utilities import time_helper

class Scheduler:
    def __init__(self, planner: PlannerBase, sch_options: dict):
        self.__planner = planner
        self.__sch_options = sch_options

    def create_schedule(self, sch_inp: ScheduleInput):
        handler_order = [
            SetupHandler().with_input(self.__planner, sch_inp, self.__sch_options),
            DeterminateDecideCandidateHandler(),
            IndeterminatePlanningHandler(),
            DeterminatePlanningHandler(),
            ResolveConflictHandler(),
            TerminationHandler()
        ]

        sch_builder = ScheduleBuilder()
        sch_req = ScheduleRequest(sch_builder)
        linked_handlers = link_handler_chain(handler_order)
        run_handler_chain(linked_handlers, sch_req)
        schedule = sch_req.extract_schedule()
        schedule.mark_as_built()
        return schedule
