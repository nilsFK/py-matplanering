#!/usr/bin/env python
# -*- coding: utf-8 -*-
from abc import (ABCMeta, abstractmethod)

from py_matplanering.core.schedule import ScheduleEvent

class BoundaryBase(metaclass=ABCMeta):
    def set_boundary(self, boundary):
        self.boundary = boundary

    @abstractmethod
    def match_event(self, sch_event: ScheduleEvent, dates: list) -> list:
        """ Match event against boundary and dates.
            Return all matching dates. """
        pass
