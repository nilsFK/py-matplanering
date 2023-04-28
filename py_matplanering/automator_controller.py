#!/usr/bin/env python
# -*- coding: utf-8 -*-

from py_matplanering.core.schedule.schedule import Schedule
from py_matplanering.core.schedule.schedule_input import ScheduleInput
from py_matplanering.core.validator import Validator
from py_matplanering.core.scheduler import Scheduler
from py_matplanering.core.planner.planner_base import PlannerBase
from py_matplanering.core.error import BaseError

from py_matplanering.utilities.logger import Logger, LoggerLevel

from typing import Any

class AutomatorControllerError(BaseError):
    def __init__(self, message, capture_data = {}):
        super(AutomatorControllerError, self).__init__(message)
        self.capture_data = capture_data

    def __str__(self):
        return self.message

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
        self.__initial_schedule = None

    def get_build_error(self, col=None) -> Any:
        if not self.__built_run:
            raise AutomatorControllerError('Attempting to get build error failed. Run build() before retrieving any errors.')
        if col is None:
            return self.__build_error
        return self.__build_error[col]

    def set_planner(self, planner: PlannerBase):
        Logger.log('Setting planner to %s' % (planner), LoggerLevel.DEBUG)
        self.__planner = planner

    def init_schedule(self, sch: Schedule):
        """ Initial schedule which may already contain events """
        self.__initial_schedule = sch

    def build(self, event_data: dict, rule_set: list) -> Any:
        self.__built_run = True
        # Inject global rules into event data.
        # Find all names of global rules
        global_rules = set()
        for rule_data in rule_set:
            if rule_data['scope'] != 'global':
                continue
            for rule_set_data in rule_data['rule_set']:
                global_rules.add(rule_set_data['name'])
        for event in event_data['data']:
            event['rules'].extend(list(global_rules))
            event['rules'] = list(set(event['rules']))
        inp = ScheduleInput(event_data, rule_set, self.__initial_schedule)
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
        scheduler = Scheduler(self.__planner, self.__sch_options, self.__initial_schedule)
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
