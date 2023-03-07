#!/usr/bin/env python
# -*- coding: utf-8 -*-

from py_matplanering.core.handler.handler import AbstractHandler

from typing import (Any)

class DeterminateDecideCandidateHandler(AbstractHandler):
    """ Handles building determinate candidates. """
    def handle(self, request: Any) ->  Any:
        sch_builder = request.get_schedule_builder()
        boundaries = sch_builder.load_boundaries()
        sch_builder.set_boundaries(boundaries)
        if sch_builder.allow_build_candidates():
            def match_boundary_cb(boundary_obj):
                return boundary_obj.get_boundary_class() == 'determinate'
            determ_candidates = sch_builder.build_candidates(boundaries, match_boundary_cb=match_boundary_cb)
            request.set_payload(determ_candidates)
        return super().handle(request)