#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Core
from py_matplanering.core.schedule.schedule_input import ScheduleInput
from py_matplanering.core.schedule.schedule_request import ScheduleRequest
from py_matplanering.core.schedule.schedule_builder import ScheduleBuilder
from py_matplanering.core.schedule.schedule import Schedule
from py_matplanering.core.planner.planner_base import PlannerBase
from py_matplanering.core.error import BaseError
# Handlers
from py_matplanering.core.handler.impl.setup_handler import (SetupHandler)
from py_matplanering.core.handler.impl.determinate_decide_candidate_handler import (
    DeterminateDecideCandidateHandler
)
from py_matplanering.core.handler.impl.indeterminate_planning_handler import (
    IndeterminatePlanningHandler
)
from py_matplanering.core.handler.impl.determinate_planning_handler import (
    DeterminatePlanningHandler
)
from py_matplanering.core.handler.impl.resolve_conflict_handler import (ResolveConflictHandler)
from py_matplanering.core.handler.impl.termination_handler import (TerminationHandler)
from py_matplanering.core.handler.handler_helper import (
    link_handler_chain,
    run_handler_chain
)
# Utilities
from py_matplanering.utilities import time_helper, misc
from py_matplanering.utilities.logger import Logger, LoggerLevel

class SchedulerError(BaseError):
    def __init__(self, message, capture_data = {}):
        super(SchedulerError, self).__init__(message)
        self.capture_data = capture_data

    def __str__(self):
        return self.message

class Scheduler:
    def __init__(self, planner: PlannerBase, sch_options: dict, init_sch: Schedule=None):
        self.__planner = planner
        self.__sch_options = sch_options
        self.__init_sch = init_sch
        self.__strategy = misc.BuildStrategy.IGNORE_CONNECTED_DAYS
        self.__pre_processed = False

    def set_strategy(self, strategy: misc.BuildStrategy):
        self.__strategy = strategy

    def pre_process(self):
        """ Any kind of pre processing of planner, schedule options or init schedule
        goes into this method. This method can only be executed once. """
        if self.__pre_processed:
            raise SchedulerError('Scheduler has already executed pre_process()')
        if self.__init_sch:
            if self.__strategy == misc.BuildStrategy.IGNORE_CONNECTED_DAYS:
                Logger.log('Running build strategy: IGNORE_CONNECTED_DAYS', LoggerLevel.DEBUG)
                pass # Do nothing, connected days will be ignored
            elif self.__strategy == misc.BuildStrategy.REPLACE_CONNECTED_DAYS:
                Logger.log('Running build strategy: REPLACE_CONNECTED_DAYS', LoggerLevel.DEBUG)
                planning_startdate, planning_enddate = self.__sch_options['planning_range']
                pr = time_helper.get_date_range(planning_startdate, planning_enddate)
                cleared_dates = []
                for date in pr:
                    cleared = self.__init_sch.clear_day(date)
                    if cleared:
                        cleared_dates.append(date)
                Logger.log('Dates with events cleared within planning range: %s' % (cleared_dates), LoggerLevel.DEBUG)

    def create_schedule(self, sch_inp: ScheduleInput) -> Schedule:
        handler_order = [
            SetupHandler().with_input(self.__planner, sch_inp, self.__sch_options, self.__init_sch),
            DeterminateDecideCandidateHandler(),
            IndeterminatePlanningHandler(),
            DeterminatePlanningHandler(),
            ResolveConflictHandler(),
            TerminationHandler()
        ]

        Logger.log('Create ScheduleBuilder', LoggerLevel.DEBUG)
        sch_builder = ScheduleBuilder()
        Logger.log('Create ScheduleRequest', LoggerLevel.DEBUG)
        sch_req = ScheduleRequest(sch_builder)
        linked_handlers = link_handler_chain(handler_order)
        Logger.log('Run defined handler chain', LoggerLevel.DEBUG)
        run_handler_chain(linked_handlers, sch_req)
        schedule = sch_req.extract_schedule()
        schedule.mark_as_built()
        return schedule
