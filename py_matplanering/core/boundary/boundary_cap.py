#!/usr/bin/env python
# -*- coding: utf-8 -*-
from py_matplanering.core.boundary.boundary_base import BoundaryBase

class BoundaryCap(BoundaryBase):
    def match_event(self, event: dict, dates: list) -> list:
        # TODO
        print("Trying to match event:", event, "with dates", dates, "against", self.boundary)
        return []
