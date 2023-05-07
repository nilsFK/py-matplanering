#!/usr/bin/env python
# -*- coding: utf-8 -*-

from py_matplanering.core.schedule.schedule import Schedule
from py_matplanering.core.schedule.schedule_input import ScheduleInput
from py_matplanering.core.validator import Validator
from py_matplanering.core.scheduler import Scheduler
from py_matplanering.core.planner.planner_base import PlannerBase
from py_matplanering.core.error import BaseError

from py_matplanering.utilities.logger import Logger, LoggerLevel
from py_matplanering.utilities import schedule_helper
from py_matplanering.utilities import misc

from typing import Any

class AutomatorControllerError(BaseError):
    def __init__(self, message, capture_data = {}):
        super(AutomatorControllerError, self).__init__(message)
        self.capture_data = capture_data

    def __str__(self):
        return self.message

class AutomatorController:
    """
        AutomatorController is the starting point for the shceduling process
        and it delegates tasks to other classes.
        It does not implement any business logic, it mainly
        setups the different parts needed for scheduling, validation,
        and so on.
        The main method of AutomatorController is build() which accepts
        event data and rule set which together produce an instance of a Schedule.
    """
    def __init__(self, sch_range: tuple, sch_options: dict={}, build_options: dict={}):
        self.__build_error = None
        self.__built_run = False
        self.__sch_options = dict(
            schedule_range=sch_range,
            planning_range=None, # None => planning range is same as schedule range
            include_props=None, # None => include all props, [] => exclude all props
            daily_event_limit=None
        )
        self.__sch_options.update(sch_options)
        self.__initial_schedule = None
        self.__build_options = dict(
            iterations=1,
            strategy=misc.BuildStrategy.IGNORE_CONNECTED_DAYS
        )
        self.__build_options.update(build_options)
        if self.__build_options['iterations'] == 0:
            raise AutomatorControllerError('Build iterations set to zero. Expected: positive integer')

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

    def set_build_option(self, build_key: str, build_val: Any):
        self.__build_options[build_key] = build_val

    def build(self, event_data: dict, rule_set: list) -> Any:
        self.__built_run = True
        # Inject global rules into event data.
        # Find all names of global rules
        global_rules = set()
        for rule_data in rule_set:
            if rule_data['scope'] == 'global':
                for rule_set_data in rule_data['rule_set']:
                    global_rules.add(rule_set_data['name'])
        for event in event_data['data']:
            event['rules'].extend(list(global_rules))
            event['rules'] = list(set(event['rules']))
        inp = ScheduleInput(event_data, rule_set, self.__initial_schedule)
        validator = Validator()
        is_valid, validation_rs, validation_msg = validator.pre_validate(inp, self.__sch_options)
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
        scheduler.set_strategy(self.__build_options['strategy'])
        scheduler.pre_process()

        Logger.log('Create Schedule', verbosity=LoggerLevel.DEBUG)
        schedule = None
        for idx in range(self.__build_options['iterations']):
            Logger.log('Running iteration: %s/%s' % (idx+1, self.__build_options['iterations']), LoggerLevel.DEBUG)
            if idx > 0:
                # feed back created schedule to scheduler which restarts the scheduling process
                inp.set_init_schedule(schedule)
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
            if schedule_helper.is_schedule_complete(schedule):
                break
        return schedule
