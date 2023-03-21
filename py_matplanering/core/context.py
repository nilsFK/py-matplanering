#!/usr/bin/env python
# -*- coding: utf-8 -*-

from py_matplanering.core.schedule.schedule import Schedule, ScheduleEvent
from py_matplanering.core.schedule.schedule_manager import ScheduleManager

from typing import Any, Union, List

# A context which holds one instance of a Schedule and any
# data which is related to but not itself contained within Schedule.
# ScheduleContext can be passed as a parameter and is a working
# data class. It may be subclassed to provide
# more specific context.
class Context:
    def __init__(self, context: Any):
        self._context = context

    def get_context(self) -> Any:
        return self._context

    def _set_context(self, context: Any):
        self._context = context

class BoundaryContext(Context):
    def __init__(self, sch_source: Union[Schedule,ScheduleManager], sch_events: List[ScheduleEvent], dates: List[str]):
        if not isinstance(sch_events, list):
            raise Exception('Unexpected sch_event is not List[ScheduleEvent]. Instead got: %s' % (sch_events))
        if not isinstance(dates, list):
            raise Exception('Unexpected dates is not a List[str]. Instead got: ' % (dates))
        self._set_context(dict(
            sch_source=sch_source,
            sch_events=sch_events,
            dates=dates
        ))

    def extract_schedule_manager(self) -> ScheduleManager:
        if isinstance(self._context['sch_source'], ScheduleManager):
            return self._context['sch_source']
        raise Exception('Schedule source is not instance of ScheduleManager, instead got: %s' % (self._context['sch_source']))

    def extract_schedule(self) -> Schedule:
        if isinstance(self._context['sch_source'], Schedule):
            return self._context['sch_source']
        raise Exception('Schedule source is not instance of Schedule, instead got: %s' % (self._context['sch_source']))

    def get_schedule_events(self) -> List[ScheduleEvent]:
        return self._context['sch_events']

    def get_dates(self) -> List[str]:
        return self._context['dates']
