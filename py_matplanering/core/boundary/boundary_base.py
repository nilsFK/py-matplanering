#!/usr/bin/env python
# -*- coding: utf-8 -*-
from abc import (ABCMeta, abstractmethod)

class BoundaryBase(metaclass=ABCMeta):
    def set_boundary(self, boundary):
        self.boundary = boundary

    @abstractmethod
    def match_event(self, event: dict, dates: list) -> list:
        """ Match event against boundary and dates.
            Return all matching dates. """
        pass
