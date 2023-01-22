#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from py_matplanering.core.input import Input
from py_matplanering.core.validator import Validator
from py_matplanering.core.scheduler import Scheduler
from py_matplanering.core.planner.planner_randomizer import PlannerRandomizer
from typing import Any

class AutomatorController:
    def __init__(self):
        self.__build_error = None
        self.__built_run = False

    def get_build_error(self, col=None) -> Any:
        if not self.__built_run:
            raise Exception('Attempting to get build error failed. Run build() before retrieving any errors.')
        if col is None:
            return self.__build_error
        return self.__build_error[col]

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
            return False

        scheduler = Scheduler(PlannerRandomizer())
        schedule = scheduler.create_schedule(inp)
        return schedule
