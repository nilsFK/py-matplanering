#!/usr/bin/env python
# -*- coding: utf-8 -*-

from py_matplanering.core.schedule.schedule import Schedule, ScheduleEvent
from py_matplanering.core.schedule.schedule_manager import ScheduleManager
from py_matplanering.core.error import BaseError

from typing import Any, Union, List

class ContextError(BaseError):
    def __init__(self, message, capture_data = {}):
        super(ContextError, self).__init__(message)
        self.capture_data = capture_data

    def __str__(self):
        return self.message

class Context:
    """ Context used to pass parameters as objects.
        Context itself doesn't actually contain any specific context
        and should be subclassed to provide some sort of context
        in the constructor. """
    def __init__(self, context: Any):
        self._context = context

    def get_context(self) -> Any:
        return self._context

    def _set_context(self, context: Any):
        self._context = context

class BoundaryContext(Context):
    """ A context which holds one instance of a Schedule or ScheduleManager and any
        data which is related to but not itself contained within Schedule.
    """
    def __init__(self, sch_source: Union[Schedule,ScheduleManager], sch_events: List[ScheduleEvent], dates: List[str]):
        if not isinstance(sch_events, list):
            raise ContextError('Unexpected sch_event is not List[ScheduleEvent]. Instead got: %s' % (sch_events))
        if not isinstance(dates, list):
            raise ContextError('Unexpected dates is not a List[str]. Instead got: ' % (dates))
        self._set_context(dict(
            sch_source=sch_source,
            sch_events=sch_events,
            dates=dates
        ))

    def extract_schedule_manager(self) -> ScheduleManager:
        if isinstance(self._context['sch_source'], ScheduleManager):
            return self._context['sch_source']
        raise ContextError('Schedule source is not instance of ScheduleManager, instead got: %s' % (self._context['sch_source']))

    def extract_schedule(self) -> Schedule:
        if isinstance(self._context['sch_source'], Schedule):
            return self._context['sch_source']
        raise ContextError('Schedule source is not instance of Schedule, instead got: %s' % (self._context['sch_source']))

    def get_schedule_events(self) -> List[ScheduleEvent]:
        return self._context['sch_events']

    def get_dates(self) -> List[str]:
        return self._context['dates']
