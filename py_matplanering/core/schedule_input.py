#!/usr/bin/env python
# -*- coding: utf-8 -*-

class ScheduleInput:
    def __init__(self, event_data: dict, rule_set: dict):
        self.event_data = event_data
        self.rule_set = rule_set

    def get_event_data(self):
        return self.event_data

    def get_rule_set(self):
        return self.rule_set
