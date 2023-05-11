#!/usr/bin/env python
# -*- coding: utf-8 -*-

from py_matplanering.core.handler.handler import AbstractHandler
from py_matplanering.core.schedule.schedule_request import ScheduleRequest
from py_matplanering.core.schedule.schedule_input import ScheduleInput
from py_matplanering.core.schedule.schedule import Schedule
from py_matplanering.core.planner.planner_base import PlannerBase

from py_matplanering.utilities.logger import Logger, LoggerLevel
from py_matplanering.utilities import schedule_helper

from typing import (Any)

class SetupHandler(AbstractHandler):
    """ Handles initial setup of required objects such as builders and so on.
        (should be first handler) """
    def with_input(self, planner: PlannerBase, sch_inp: ScheduleInput, sch_options: dict={}, init_sch: Schedule=None):
        self.__planner = planner
        self.__sch_inp = sch_inp
        self.__sch_options = sch_options
        self.__init_sch = init_sch
        return self

    def handle(self, request: Any) -> Any:
        Logger.log('Running handler', verbosity=LoggerLevel.DEBUG)
        sch_builder = request.get_schedule_builder()
        sch_builder.set_planner(self.__planner)
        sch_builder.set_schedule_input(self.__sch_inp)
        schedule = self.__planner.plan_init(self.__sch_options, self.__init_sch)
        sch_builder.set_schedule(schedule)
        filter_functions = [
            schedule_helper.filter_events_by_planning_interval,
            schedule_helper.filter_events_by_placing,
            schedule_helper.filter_events_by_date_interval,
            schedule_helper.filter_events_by_distance,
            schedule_helper.filter_events_by_quota
        ]
        for filter_fn in filter_functions:
            Logger.log('Registering filter event function: %s' % (filter_fn), LoggerLevel.DEBUG)
            sch_builder.register_filter_event_function(filter_fn)
        return super().handle(request)
