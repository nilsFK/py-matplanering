#!/usr/bin/env python
# -*- coding: utf-8 -*-

from py_matplanering.core.input import Input

class Validator:
    @staticmethod
    def __validate_tagged_data(tagged_data: dict) -> dict:
        rs = dict(ok=True, data=None, msg=None)
        return rs

    @staticmethod
    def __validate_rule_set(rule_set: dict) -> dict:
        rs = dict(ok=True, data=None, ms=None)
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