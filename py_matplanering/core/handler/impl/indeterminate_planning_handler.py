#!/usr/bin/env python
# -*- coding: utf-8 -*-

from py_matplanering.core.handler.handler import AbstractHandler

from typing import (Any)

class IndeterminatePlanningHandler(AbstractHandler):
    """ Handles planning determinate candidates into schedule events. """
    def handle(self, request: Any) ->  Any:
        sch_builder = request.get_schedule_builder()
        determ_candidates = request.get_payload()
        sch_builder.plan_indeterminate_schedule(determ_candidates)
        return super().handle(request)
