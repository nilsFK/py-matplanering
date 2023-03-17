#!/usr/bin/env python
# -*- coding: utf-8 -*-

from py_matplanering.core.schedule.schedule_input import ScheduleInput
from py_matplanering.core.validator import Validator
from py_matplanering.core.scheduler import Scheduler
from py_matplanering.core.planner.planner_base import PlannerBase

from py_matplanering.utilities.logger import Logger, LoggerLevel

from typing import Any

class AutomatorController:
    def __init__(self, startdate: str, enddate: str, sch_options: dict={}):
        self.__build_error = None
        self.__built_run = False
        self.__sch_options = dict(
            startdate=startdate,
            enddate=enddate,
            include_props=None, # None => include all props, [] => exclude all props
            daily_event_limit=None
        )
        self.__sch_options.update(sch_options)

    def get_build_error(self, col=None) -> Any:
        if not self.__built_run:
            raise Exception('Attempting to get build error failed. Run build() before retrieving any errors.')
        if col is None:
            return self.__build_error
        return self.__build_error[col]

    def set_planner(self, planner: PlannerBase):
        Logger.log('Setting planner to %s' % (planner), LoggerLevel.DEBUG)
        self.__planner = planner

    def build(self, event_data: dict, rule_set: dict) -> Any:
        self.__built_run = True
        inp = ScheduleInput(event_data, rule_set)
        validator = Validator()
        is_valid, validation_rs, validation_msg = validator.pre_validate(inp)
        if not is_valid:
            Logger.log('Invalid ScheduleInput due to pre_validate', LoggerLevel.FATAL)
            self.__build_error = dict(
                validation_data=validation_rs,
                msg=validation_msg
            )
            assert self.__build_error['msg'] is not None
            return False
        Logger.log('Create Scheduler', verbosity=LoggerLevel.DEBUG)
        scheduler = Scheduler(self.__planner, self.__sch_options)
        Logger.log('Create Schedule', verbosity=LoggerLevel.DEBUG)
        schedule = scheduler.create_schedule(inp)

        is_valid, validation_rs, validation_msg = validator.post_validate(schedule)
        if not is_valid:
            Logger.log('Invalid Schedule due to post_validate', LoggerLevel.FATAL)
            self.__build_error = dict(
                validation_data=validation_rs,
                msg=validation_msg
            )
            assert self.__build_error['msg'] is not None
            return False

        return schedule
