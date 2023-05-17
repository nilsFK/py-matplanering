#!/usr/bin/env python
# -*- coding: utf-8 -*-

from py_matplanering.core.handler.handler import AbstractHandler
from py_matplanering.core.handler.handler_error import HandlerError
from py_matplanering.core.schedule.schedule_request import ScheduleRequest
from py_matplanering.core.schedule.schedule_input import ScheduleInput
from py_matplanering.core.schedule.schedule import Schedule
from py_matplanering.core.schedule import schedule_event_filter
from py_matplanering.core.planner.planner_base import PlannerBase

from py_matplanering.utilities.logger import Logger, LoggerLevel
from py_matplanering.utilities import schedule_helper

from typing import (Any)

class SetupHandler(AbstractHandler):
    """ Handles initial setup of required objects such as builders and so on.
        (should be first handler) """
    def with_input(self, planner: PlannerBase, sch_inp: ScheduleInput, sch_options: dict={}, init_sch: Schedule=None, sch_event_filters: list=[]):
        self.__planner = planner
        self.__sch_inp = sch_inp
        self.__sch_options = sch_options
        self.__init_sch = init_sch
        self.__custom_sch_event_filters = sch_event_filters
        return self

    def handle(self, request: Any) -> Any:
        Logger.log('Running handler', verbosity=LoggerLevel.DEBUG)
        sch_builder = request.get_schedule_builder()
        sch_builder.set_planner(self.__planner)
        sch_builder.set_schedule_input(self.__sch_inp)
        schedule = self.__planner.plan_init(self.__sch_options, self.__init_sch)
        sch_builder.set_schedule(schedule)
        # ordered filter functions by least time consuming in terms of complexity
        # to most time consuming.
        filter_objects = [
            schedule_event_filter.PlanningIntervalScheduleEventFilter(),
            schedule_event_filter.PlacingScheduleEventFilter(),
            schedule_event_filter.DateIntervalScheduleEventFilter(),
            schedule_event_filter.DistanceScheduleEventFilter(),
            schedule_event_filter.QuotaScheduleEventFilter()
        ]
        # Inject custom schedule event filters into filter_objects
        if len(self.__custom_sch_event_filters) > 0:
            filter_objects.extend(self.__custom_sch_event_filters)
        registered_names = set()
        for filter_obj in filter_objects:
            if filter_obj.get_name() in registered_names:
                raise HandlerError('Attempting to re-register filter schedule event function: %s' % (filter_obj.get_name()))
            Logger.log('Registering filter event function: %s' % (filter_obj.get_name()), LoggerLevel.DEBUG)
            sch_builder.register_filter_event_function(filter_obj.get_filter_function())
            registered_names.add(filter_obj.get_name())
        return super().handle(request)
