#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Input:
    def __init__(self, tagged_data: dict, rule_set: dict):
        self.tagged_data = tagged_data
        self.rule_set = rule_set

    def get_tagged_data(self):
        return self.tagged_data

    def get_rule_set(self):
        return self.rule_set
