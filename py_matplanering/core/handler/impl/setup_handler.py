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