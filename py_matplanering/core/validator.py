#!/usr/bin/env python
# -*- coding: utf-8 -*-

from py_matplanering.core.schedule.schedule_input import ScheduleInput
from py_matplanering.core.schedule.schedule import Schedule
from py_matplanering.core.error import BaseError

from py_matplanering.utilities.logger import Logger, LoggerLevel

from typing import Any

class ValidatorError(BaseError):
    def __init__(self, message, capture_data = {}):
        super(ValidatorError, self).__init__(message)
        self.capture_data = capture_data

    def __str__(self):
        return self.message

class Validator:

    @staticmethod
    def report_error(err_msg: str, index: int=None, error_container: dict=None, id_: int=None) -> Any:
        if not isinstance(error_container, dict):
            raise ValidatorError('Expected error_container to be dict, instead got: %s' % (type(error_container)))
        full_err_msg = 'Validation error: %s' % (err_msg)
        if index:
            full_err_msg += ' at index position: %s' % (index)
        if id_:
            full_err_msg += ' (with row id: %s)' % (id_)
        if error_container:
            error_container['error'] = True
            error_container['msg'] = full_err_msg
            return error_container
        return full_err_msg


    @staticmethod
    def __validate_event_data(event_data: dict) -> dict:
        rs = dict(ok=False, data=event_data, msg=None)
        if len(event_data) == 0:
            return Validator.report_error('event_data is empty', error_container=rs)
        if not event_data.get('data'):
            return Validator.report_error('event_data is missing required property "data"', error_container=rs)
        required_props = ['id', 'name']
        ids = set()
        for idx, row in enumerate(event_data['data']):
            for prop in required_props:
                if not row.get(prop):
                    return Validator.report_error('event_data->data is missing required property "{prop}"'.format(**{'prop': prop}), index=idx, error_container=rs, id_=row['id'])
            if row['id'] in ids:
                return Validator.report_error('Multiple instances of events with same id', error_container=rs, id_=row['id'])
            ids.add(row['id'])
        if rs['ok'] and rs['msg']:
            raise ValidatorError('Validation error: marked as OK but contains error msg. Expected msg=None, instead got: %s' % (rs['msg']))
        rs['ok'] = True
        return rs

    @staticmethod
    def __validate_rule_set(rule_set: dict) -> dict:
        rs = dict(ok=False, data=rule_set, msg=None)
        if len(rule_set) == 0:
            return Validator.report_error('rule_set is empty', error_container=rs)
        if not rule_set.get('name'):
            return Validator.report_error('rule_set is missing required property "name"', error_container=rs)
        if not rule_set.get('rule_set'):
            return Validator.report_error('rule_set is missing required property "rule_set"', error_container=rs)
        required_props = ['name', 'rules']
        for idx, row in enumerate(rule_set['rule_set']):
            id_ = row['id']
            for prop in required_props:
                if not row.get(prop):
                    return Validator.report_error('rule_set->rule_set is missing required property "{prop}"'.format(**{'prop': prop}), index=idx, error_container=rs, id_=id_)
            if not isinstance(row['rules'], list):
                return Validator.report_error('rule_set->rule_set.rules is not a list', index=idx, error_container=rs, id_=id_)
            if len(row['rules']) == 0:
                return Validator.report_error('rule_set->rule_set.rules is empty', index=idx, error_container=rs, id_=id_)
        if rs['ok'] and rs['msg']:
            raise ValidatorError('Validation error: marked as OK but contains msg. Expected msg=None, instead got: %s' % (rs['msg']))
        rs['ok'] = True
        return rs

    @staticmethod
    def __validate_initial_schedule(init_sch: Schedule, event_data: dict) -> dict:
        rs = dict(ok=False, data=init_sch, msg=None)
        init_sch_event_ids = list(set([event.get_id() for event in init_sch.get_events()]))

        event_pool_sch_event_ids = []
        for event_row in event_data['data']:
            event_pool_sch_event_ids.append(event_row['id'])
        for idx, init_sch_event_id in enumerate(init_sch_event_ids):
            if init_sch_event_id not in event_pool_sch_event_ids:
                return Validator.report_error('Initial schedule (init_sch) contains event id missing from event pool', index=idx, error_container=rs, id_=init_sch_event_id)
        if rs['ok'] and rs['msg']:
            raise ValidatorError('Validation error: marked as OK but contains msg. Expected msg=None, instead got: %s' % (rs['msg']))
        rs['ok'] = True
        return rs

    @staticmethod
    def pre_validate(inp: ScheduleInput) -> tuple:
        Logger.log('Running input through pre validation method', verbosity=LoggerLevel.DEBUG)

        # Validate: rule set
        # ==================
        for rule_set_dct in inp.get_org_rule_set():
            validation_rule_set = Validator.__validate_rule_set(rule_set_dct)
            if not validation_rule_set['ok']:
                return (False, validation_rule_set['data'], validation_rule_set['msg'])

        # Validate: event data
        # ====================
        validation_event_data = Validator.__validate_event_data(inp.get_org_event_data())
        if not validation_event_data['ok']:
            return (False, validation_event_data['data'], validation_event_data['msg'])

        # Validate: schedule
        # ==================
        if inp.get_init_schedule():
            validation_init_sch = Validator.__validate_initial_schedule(inp.get_init_schedule(), inp.get_org_event_data())
            if not validation_init_sch['ok']:
                return (False, validation_init_sch['data'], validation_init_sch['msg'])

        # All validation OK
        return (True, None, None)

    @staticmethod
    def post_validate(sch: Schedule) -> tuple:
        Logger.log('Running input through post validation method', verbosity=LoggerLevel.DEBUG)
        return (True, None, None) # nothing validated for now
