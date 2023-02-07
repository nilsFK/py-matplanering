#!/usr/bin/env python
# -*- coding: utf-8 -*-

from py_matplanering.core.schedule.schedule_builder import ScheduleBuilder

class ScheduleRequest:
    def __init__(self, sch_builder: ScheduleBuilder):
        self.sch_builder = sch_builder

    def extract_schedule(self):
        return self.sch_builder.extract_schedule()

    def get_schedule_builder(self):
        return self.sch_builder
