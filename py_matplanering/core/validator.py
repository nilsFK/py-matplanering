#!/usr/bin/env python
# -*- coding: utf-8 -*-

from py_matplanering.core.schedule_input import ScheduleInput
from py_matplanering.core.schedule import Schedule

from typing import Any


class Validator:

    @staticmethod
    def report_error(err_msg: str, index: int=None, error_container: dict=None, id_: int=None) -> Any:
        full_err_msg = 'Validation error: %s' % (err_msg)
        if index:
            full_err_msg += ' at index position: %s' % (index)
        if id_:
            full_err_msg += ' (with row id: %s)' % (id_)
        if error_container:
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
        required_props = ['name']
        for idx, row in enumerate(event_data['data']):
            for prop in required_props:
                if not row.get(prop):
                    return Validator.report_error('event_data->rule_set.data is missing required property "{prop}"'.format(**{'prop': prop}), index=idx, error_container=rs, id_=row['id'])
        if rs['ok'] and rs['msg']:
            raise Exception('Validation error: marked as OK but contains error msg. Expected msg=None, instead got: %s' % (rs['msg']))
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
            raise Exception('Validation error: marked as OK but contains msg. Expected msg=None, instead got: %s' % (rs['msg']))
        rs['ok'] = True
        return rs

    @staticmethod
    def pre_validate(inp: ScheduleInput) -> tuple:
        validation_rule_set = Validator.__validate_rule_set(inp.get_rule_set())
        if not validation_rule_set['ok']:
            return (False, validation_rule_set['data'], validation_rule_set['msg'])
        validation_event_data = Validator.__validate_event_data(inp.get_event_data())
        if not validation_event_data['ok']:
            return (False, validation_event_data['data'], validation_event_data['msg'])
        return (True, None, None)

    @staticmethod
    def post_validate(sch: Schedule) -> tuple:
        return (True, None, None) # nothing validated for now
