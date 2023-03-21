#!/usr/bin/env python
# -*- coding: utf-8 -*-
from abc import (ABCMeta, abstractmethod)

from py_matplanering.core.schedule.schedule import ScheduleEvent
from py_matplanering.core.context import BoundaryContext

from typing import List


class BoundaryBase(metaclass=ABCMeta):
    def set_boundary(self, boundary):
        self._boundary = boundary

    def get_boundary(self):
        return self._boundary

    def filter_eligible_dates(self, boundary_context: BoundaryContext) -> List[str]:
        """ Filter all eligible dates from context.
            Returns all matching dates. """
        return boundary_context.get_dates()

    def filter_eligible_events(self, boundary_context: BoundaryContext) -> List[ScheduleEvent]:
        """ Filter all eligible events from context.
            Returns all matching events. """
        return boundary_context.get_schedule_events()

    @abstractmethod
    def get_boundary_class(self) -> str:
        pass
