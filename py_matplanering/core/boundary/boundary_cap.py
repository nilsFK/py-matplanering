#!/usr/bin/env python
# -*- coding: utf-8 -*-
from py_matplanering.core.boundary.boundary_base import BoundaryBase

class BoundaryCap(BoundaryBase):
    def match_event(self, event: dict, dates: list) -> list:
        return dates # match all dates since it's indeterminate

    def get_boundary_class(self) -> str:
        return 'indeterminate'
