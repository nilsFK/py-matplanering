#!/usr/bin/env python
# -*- coding: utf-8 -*-

from py_matplanering.core.handler.handler import AbstractHandler

from py_matplanering.utilities.logger import Logger, LoggerLevel

from typing import (Any)

class TerminationHandler(AbstractHandler):
    """ Handles terminal actions (should be last handler). """
    def handle(self, request: Any) -> Any:
        Logger.log('Running handler', verbosity=LoggerLevel.DEBUG)
        sch_builder = request.get_schedule_builder()
        sch_builder.build()
        return None
