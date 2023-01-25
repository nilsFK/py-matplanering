#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from py_matplanering.core.input import Input
from py_matplanering.core.validator import Validator
from py_matplanering.core.scheduler import Scheduler
from py_matplanering.core.planner.planner_base import PlannerBase
from typing import Any

class AutomatorController:
    def __init__(self, startdate: str, enddate: str):
        self.__build_error = None
        self.__built_run = False
        self.__sch_options = dict(
            startdate=startdate,
            enddate=enddate
        )

    def get_build_error(self, col=None) -> Any:
        if not self.__built_run:
            raise Exception('Attempting to get build error failed. Run build() before retrieving any errors.')
        if col is None:
            return self.__build_error
        return self.__build_error[col]

    def set_planner(self, planner: PlannerBase):
        self.__planner = planner

    def build(self, tagged_data: dict, rule_set: dict) -> Any:
        self.__built_run = True
        inp = Input(tagged_data, rule_set)
        validator = Validator()
        is_valid, validation_rs, validation_msg = validator.validate(inp)
        if not is_valid:
            self.__build_error = dict(
                validation_data=validation_rs,
                msg=validation_msg
            )
            assert self.__build_error['msg'] is not None
            return False

        scheduler = Scheduler(self.__planner, self.__sch_options)
        schedule = scheduler.create_schedule(inp)
        return schedule
