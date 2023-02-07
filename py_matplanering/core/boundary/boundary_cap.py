#!/usr/bin/env python
# -*- coding: utf-8 -*-
from py_matplanering.core.boundary.boundary_base import BoundaryBase

class BoundaryCap(BoundaryBase):
    def match_event(self, event: dict, dates: list) -> list:
        matching_dates = []
        print("Trying to match event:", event, "with dates", dates, "against", self.boundary)

        # TODO: check caps.
        # TODO: if cap is min - check if event has been scheduled less than min. If so,
        # schedule event
        cap_list = self.boundary['cap']
        for cap in cap_list:
            cap_val = cap['max']
            cap_unit = cap['time_unit']
            print(cap_val, cap_unit)
        # import sys; sys.exit()
        return [] # TODO fix
