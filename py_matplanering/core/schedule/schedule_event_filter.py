#!/usr/bin/env python
# -*- coding: utf-8 -*-
# from __future__ import annotations

from py_matplanering.core.schedule.schedule import Schedule, ScheduleEvent
from py_matplanering.core.context import BoundaryContext, ScheduleEventFilterContext

from typing import Callable, List

from abc import (ABCMeta, abstractmethod)

class BaseScheduleEventFilter(metaclass=ABCMeta):
    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_filter_function(self) -> Callable:
        pass

class PlanningIntervalScheduleEventFilter(BaseScheduleEventFilter):
    def get_name(self) -> str:
        return 'default__planning_interval_sch_event_filter'

    def get_filter_function(self) -> Callable:
        def filter_fn(ctx: ScheduleEventFilterContext) -> List[ScheduleEvent]:
            """ Checks if date is within planning interval. If so, return all events.
            Otherwise, return empty list. """
            if ctx.get_date() > ctx.get_schedule().get_planning_enddate():
                return []
            if ctx.get_date() < ctx.get_schedule().get_planning_startdate():
                return []
            # date is within planning interval, return all events
            return ctx.get_schedule_events()
        return filter_fn

class PlacingScheduleEventFilter(BaseScheduleEventFilter):
    def get_name(self) -> str:
        return 'default__placing_sch_event_filter'

    def get_filter_function(self) -> Callable:
        def filter_fn(ctx: ScheduleEventFilterContext) -> List[ScheduleEvent]:
            """ Returns empty list if date has been placed in schedule (sch) """
            placed_events = ctx.get_schedule().get_events_by_date(ctx.get_date())
            if len(placed_events) > 0:
                return []
            # date has not been placed in sch, return all events
            return ctx.get_schedule_events()
        return filter_fn

class DateIntervalScheduleEventFilter(BaseScheduleEventFilter):
    def get_name(self) -> str:
        return 'default__date_interval_sch_event_filter'

    def get_filter_function(self) -> Callable:
        def filter_fn(ctx: ScheduleEventFilterContext) -> List[ScheduleEvent]:
            """ Events can be restricted to a given period (min, max) where planning is allowed.
                Checks if date is within the event date period restriction. """
            filtered_sch_events = []
            for event in ctx.get_schedule_events():
                mindate, maxdate = event.get_mindate(), event.get_maxdate()
                if mindate is None and maxdate is None:
                    filtered_sch_events.append(event)
                    continue
                if maxdate and ctx.get_date() > maxdate:
                    continue
                if mindate and ctx.get_date() < mindate:
                    continue
                filtered_sch_events.append(event)
            return filtered_sch_events
        return filter_fn

class QuotaScheduleEventFilter(BaseScheduleEventFilter):
    def get_name(self) -> str:
        return 'default__quota_sch_event_filter'

    def get_filter_function(self) -> Callable:
        def filter_fn(ctx: ScheduleEventFilterContext) -> List[ScheduleEvent]:
            filtered_sch_events = []
            for event in ctx.get_schedule_events():
                ok, *_ = ctx.get_schedule().validate_quota(event, ctx.get_date())
                if ok:
                    filtered_sch_events.append(event)
            return filtered_sch_events
        return filter_fn

class DistanceScheduleEventFilter(BaseScheduleEventFilter):
    def get_name(self) -> str:
        return 'default__distance_sch_event_filter'

    def get_filter_function(self) -> Callable:
        def filter_fn(ctx: ScheduleEventFilterContext) -> List[ScheduleEvent]:
            filtered_sch_events = []
            for sch_event in ctx.get_schedule_events():
                event_ok = True
                for boundary in sch_event.get_boundaries():
                    if boundary.get_boundary_class() == 'distance':
                        boundary_ctx = BoundaryContext(ctx.get_schedule(), [sch_event], [ctx.get_date()])
                        ok_events = boundary.filter_eligible_events(boundary_ctx)
                        if len(ok_events) == 0:
                            event_ok = False
                            break
                if event_ok:
                    filtered_sch_events.append(sch_event)
            return filtered_sch_events
        return filter_fn

class ExcludeEventIdsScheduleEventFilter(BaseScheduleEventFilter):
    def __init__(self, exclude_event_ids: list):
        self.__exclude_event_ids = exclude_event_ids

    def get_name(self) -> str:
        return 'default__exclude_event_ids_schedule_event_filter'

    def get_filter_function(self) -> Callable:
        def filter_fn(ctx: ScheduleEventFilterContext) -> List[ScheduleEvent]:
            if len(self.__exclude_event_ids) == 0:
                return ctx.get_schedule_events()
            filtered_sch_events = []
            for sch_event in ctx.get_schedule_events():
                if sch_event.get_id() in self.__exclude_event_ids:
                    continue
                filtered_sch_events.append(sch_event)
            return filtered_sch_events
        return filter_fn

class CustomScheduleEventFilter(BaseScheduleEventFilter):
    def __init__(self, name: str, filter_fn: Callable):
        self.__name = 'custom__%s' % (name)
        self.__filter_fn = filter_fn

    def get_name(self) -> str:
        return self.__name

    def get_filter_function(self) -> Callable:
        return self.__filter_fn
