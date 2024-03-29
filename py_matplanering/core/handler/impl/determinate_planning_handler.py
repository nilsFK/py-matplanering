#!/usr/bin/env python
# -*- coding: utf-8 -*-

from py_matplanering.core.handler.handler import AbstractHandler

from py_matplanering.utilities.logger import Logger, LoggerLevel

from typing import (Any)

class DeterminatePlanningHandler(AbstractHandler):
    """ Handles planning determinate candidates """
    def handle(self, request: Any) ->  Any:
        Logger.log('Running handler', verbosity=LoggerLevel.DEBUG)
        sch_builder = request.get_schedule_builder()
        determ_candidates = request.get_payload()
        sch_builder.plan_determinate_schedule(determ_candidates)
        return super().handle(request)
