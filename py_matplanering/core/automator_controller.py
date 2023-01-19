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
        pass

    def build(self, inp: dict, rule_set: dict) -> Any:
        inp = Input(input, rule_set)
        validator = Validator()
        is_valid = validator.validate(inp)
        if not is_valid:
            return False

        scheduler = Scheduler(PlannerRandomizer())
        schedule = scheduler.create_schedule(inp)
        return schedule
