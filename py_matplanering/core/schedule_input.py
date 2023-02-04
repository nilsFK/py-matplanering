#!/usr/bin/env python
# -*- coding: utf-8 -*-

from py_matplanering.core.schedule import ScheduleEvent

class ScheduleInput:
    def __init__(self, event_data: dict, rule_set: dict):
        self.org_event_data_dct = event_data
        self.org_rule_set_dct = rule_set
        self.event_data_lst = None
        self.rule_set_lst = None
        self.__converted = False

    def get_event_data(self) -> list:
        # Lazy convertion of event data (dict) to schedule events (list of ScheduleEvent)
        if self.__converted is False:
            tmp_event_data = []
            for row in self.org_event_data_dct['data']:
                tmp_event_data.append(ScheduleEvent(row))
            self.event_data_lst = tmp_event_data
            del tmp_event_data
            self.__converted = True
        return self.event_data_lst

    def get_org_event_data(self):
        return self.org_event_data_dct

    def get_org_rule_set(self):
        return self.org_rule_set_dct

    def get_rule_set(self):
        return self.org_rule_set_dct
