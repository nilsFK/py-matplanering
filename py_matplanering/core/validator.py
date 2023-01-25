#!/usr/bin/env python
# -*- coding: utf-8 -*-

from py_matplanering.core.input import Input

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
    def __validate_tagged_data(tagged_data: dict) -> dict:
        rs = dict(ok=False, data=tagged_data, msg=None)
        if len(tagged_data) == 0:
            return Validator.report_error('tagged_data is empty', error_container=rs)
        if not tagged_data.get('data'):
            return Validator.report_error('tagged_data is missing required property "data"', error_container=rs)
        required_props = ['name']
        for idx, row in enumerate(tagged_data['data']):
            for prop in required_props:
                if not row.get(prop):
                    return Validator.report_error('tagged_data->rule_set.data is missing required property "{prop}"'.format(**{'prop': prop}), index=idx, error_container=rs, id_=row['id'])
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
        if not rule_set.get('ruleset'):
            return Validator.report_error('rule_set is missing required property "ruleset"', error_container=rs)
        required_props = ['name', 'rules']
        for idx, row in enumerate(rule_set['ruleset']):
            id_ = row['id']
            for prop in required_props:
                if not row.get(prop):
                    return Validator.report_error('rule_set->ruleset is missing required property "{prop}"'.format(**{'prop': prop}), index=idx, error_container=rs, id_=id_)
            if not isinstance(row['rules'], list):
                return Validator.report_error('rule_set->ruleset.rules is not a list', index=idx, error_container=rs, id_=id_)
            if len(row['rules']) == 0:
                return Validator.report_error('rule_set->ruleset.rules is empty', index=idx, error_container=rs, id_=id_)
        if rs['ok'] and rs['msg']:
            raise Exception('Validation error: marked as OK but contains msg. Expected msg=None, instead got: %s' % (rs['msg']))
        rs['ok'] = True
        return rs

    @staticmethod
    def validate(inp: Input) -> tuple:
        validation_rule_set = Validator.__validate_rule_set(inp.get_rule_set())
        if not validation_rule_set['ok']:
            return (False, validation_rule_set['data'], validation_rule_set['msg'])
        validation_tagged_data = Validator.__validate_tagged_data(inp.get_tagged_data())
        if not validation_tagged_data['ok']:
            return (False, validation_tagged_data['data'], validation_tagged_data['msg'])
        return (True, None, None)
