#!/usr/bin/env python
# -*- coding: utf-8 -*-
from py_matplanering.core.boundary.boundary_base import BoundaryBase, BoundaryError
from py_matplanering.core.context import BoundaryContext
from py_matplanering.core.schedule.schedule import Schedule
from py_matplanering.core.schedule.schedule import ScheduleEvent
from py_matplanering.utilities import time_helper
from py_matplanering.utilities.logger import Logger, LoggerLevel

from typing import List


class BoundaryDistance(BoundaryBase):
    """
        Checks for conflicts between events in a time distance span.
        It measures distance between an event of the same id to the next one.
        If such an event overlaps, it will result in an event conflict.
        Distances are sequential arrows of time, both to the past and/or into
        the future.
    """
    def filter_eligible_dates(self, boundary_context: BoundaryContext) -> List[str]:
        return boundary_context.get_dates()

    def filter_eligible_events(self, boundary_context: BoundaryContext) -> List[ScheduleEvent]:
        eligible_events = []
        sch = boundary_context.extract_schedule()
        if len(boundary_context.get_dates()) > 1:
            raise NotImplementedError
        for sch_event in boundary_context.get_schedule_events():
            if not self.__has_distance_conflict(sch, boundary_context.get_dates()[0], sch_event):
                eligible_events.append(sch_event)
        return eligible_events

    def __has_distance_conflict(self, sch: Schedule, date: str, sch_event: ScheduleEvent) -> bool:
        if len(sch.get_events()) == 0: # Nothing is planned, so no conflicts possible
            return False
        grouped_events = sch.get_grouped_events(sch_event.get_id())
        for distance in self._boundary['distance']:
            if not isinstance(distance['value'], int) or isinstance(distance['value'], bool):
                raise BoundaryError('Unexpected distance value: %s (given date=%s, event id=%s, distance data=%s). Expected: int' % (distance['value'], date, sch_event.get_id(), distance))
            if distance['time_unit'] == 'day':
                days = distance['value']
            elif distance['time_unit'] == 'week':
                days = distance['value'] * 7
            elif distance['time_unit'] == 'month':
                days = distance['value'] * 30
            else:
                raise BoundaryError('Unknown distance time unit: %s (given date=%s, event id=%s, distance data=%s)' % (distance['time_unit'], date, sch_event.get_id(), distance))
            start_date = time_helper.format_date(time_helper.add_days(time_helper.parse_date(date), -days+1))
            end_date = time_helper.format_date(time_helper.add_days(time_helper.parse_date(date), +days-1))
            examine_dates = time_helper.get_date_range(start_date, end_date)
            examine_dates.remove(date)
            for exam_date in examine_dates:
                if grouped_events.get(exam_date):
                    if len(grouped_events[exam_date]) > 0:
                        Logger.log('Found distance conflict on event id=%s between %s and %s' % (sch_event.get_id(), exam_date, date), LoggerLevel.DEBUG)
                        return True
        return False

    def get_boundary_class(self) -> str:
        return 'distance'
