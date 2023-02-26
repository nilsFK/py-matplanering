#!/usr/bin/env python
# -*- coding: utf-8 -*-
from abc import (ABCMeta, abstractmethod)

from py_matplanering.core.schedule.schedule import ScheduleEvent

class BoundaryBase(metaclass=ABCMeta):
    def set_boundary(self, boundary):
        self._boundary = boundary

    def get_boundary(self):
        return self._boundary

    @abstractmethod
    def match_event(self, sch_event: ScheduleEvent, dates: list) -> list:
        """ Match event against boundary and dates.
            Returns all matching dates. """
        pass

    @abstractmethod
    def get_boundary_class(self) -> str:
        pass
