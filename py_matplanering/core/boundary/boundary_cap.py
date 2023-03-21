#!/usr/bin/env python
# -*- coding: utf-8 -*-
from py_matplanering.core.boundary.boundary_base import BoundaryBase
from py_matplanering.core.schedule.schedule import ScheduleEvent
from py_matplanering.core.context import BoundaryContext

class BoundaryCap(BoundaryBase):
    def filter_eligible_dates(self, boundary_context: BoundaryContext) -> list:
        # match all dates since it's indeterminate
        return boundary_context.get_dates()

    def get_boundary_class(self) -> str:
        return 'indeterminate'
