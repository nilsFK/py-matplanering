#!/usr/bin/env python
# -*- coding: utf-8 -*-

from py_matplanering.core.schedule.schedule import Schedule, ScheduleEvent

from typing import Union

class ScheduleInput:
    def __init__(self, event_data: dict, rule_set: Union[dict, list], init_schedule: Schedule=None):
        # Find global rules and insert those into event data
        self.org_event_data_dct = event_data
        if isinstance(rule_set, dict):
            self.org_rule_set_lst = [rule_set]
        else:
            self.org_rule_set_lst = rule_set
        self.event_data_lst = None
        self.__converted = False
        self.__require_active = False
        self.__init_schedule = init_schedule

    def get_event_data(self, require_active: bool=False, event_defaults={}) -> list:
        # Lazy convertion of event data (dict) to schedule events (list of ScheduleEvent)
        if require_active != self.__require_active:
            self.__converted = False
        if self.__converted is False:
            tmp_event_data = []
            for row in self.org_event_data_dct['data']:
                # skip inactive
                if require_active and row['active'] == 0:
                    continue
                if row.get('prio') is None:
                    row['prio'] = event_defaults.get('prio')
                tmp_event_data.append(ScheduleEvent(row))
            self.event_data_lst = tmp_event_data
            del tmp_event_data
            self.__converted = True
        self.__require_active = require_active
        return self.event_data_lst

    def get_org_event_data(self):
        return self.org_event_data_dct

    def get_org_rule_set(self) -> list:
        return self.org_rule_set_lst

    def get_rule_set(self) -> list:
        return self.org_rule_set_lst

    def get_init_schedule(self) -> Schedule:
        return self.__init_schedule

    def set_init_schedule(self, init_schedule: Schedule):
        self.__init_schedule = init_schedule
