#!/usr/bin/env python
# -*- coding: utf-8 -*-

from py_matplanering.core.schedule.schedule_builder import ScheduleBuilder

from typing import Any

class ScheduleRequest:
    def __init__(self, sch_builder: ScheduleBuilder):
        self.sch_builder = sch_builder
        self.payload = None

    def extract_schedule(self):
        return self.sch_builder.extract_schedule()

    def get_schedule_builder(self):
        return self.sch_builder

    def set_payload(self, payload: Any):
        self.payload = payload

    def get_payload(self) -> Any:
        return self.payload
