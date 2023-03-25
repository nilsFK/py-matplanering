#!/usr/bin/env python
# -*- coding: utf-8 -*-

from py_matplanering.core.handler.handler import AbstractHandler
from py_matplanering.core.schedule.schedule import ScheduleIterator

from py_matplanering.utilities.logger import Logger, LoggerLevel

from typing import Any

class ResolveConflictHandler(AbstractHandler):
    """ Resolves any conflicts created by planning handlers. """
    def handle(self, request: Any) -> Any:
        Logger.log('Running handler', verbosity=LoggerLevel.DEBUG)
        sch_builder = request.get_schedule_builder()
        determ_candidates = request.get_payload()
        opts = sch_builder.get_schedule_options()
        iter_order = list(ScheduleIterator(determ_candidates, opts.get('iter_method')))
        sch_builder.plan_resolve_conflicts(determ_candidates, iter_order=iter_order)
        return super().handle(request)
