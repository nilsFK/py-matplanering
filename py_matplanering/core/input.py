#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Input:
    def __init__(self, inp: dict, rule_set: dict):
        self.input = inp
        self.rule_set = rule_set

    def get_input(self):
        return self.input

    def get_rule_set(self):
        return self.rule_set
