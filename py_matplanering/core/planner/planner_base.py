#!/usr/bin/env python
# -*- coding: utf-8 -*-
from abc import (ABCMeta, abstractmethod)
from py_matplanering.core.schedule_input import ScheduleInput
from py_matplanering.core.schedule import Schedule

"""
    PlannerBase is an abstract base class (ABC). It does not implement
    any methods, it only specifies the method signatures for subclasses
    to implement.
    The methods deals with initializing the planning process and
    resolve any issues with scheduling.
    It is recommended to raise an exception within a method that
    should not occur.
"""
class PlannerBase(metaclass=ABCMeta):
    @abstractmethod
    def plan_init(self, inp: ScheduleInput, sch_options: dict) -> Schedule:
        """ initializes a planning session with given input and
        related schedule options. """
        pass

    @abstractmethod
    def plan_resolve_conflict(self, conflicting_events: list):
        """ if one day contains multiple events
            a conflict will surface. such conflicts needs to
            be resolved within this method.
            returns the selected event.
            """
        pass

    @abstractmethod
    def plan_missing_event(self, date: str, day_obj: dict) -> dict:
        """ occurs when a particular day is missing events.
            return one event (however not required, return
            None to skip assigning an event to that day)
        """
        pass

