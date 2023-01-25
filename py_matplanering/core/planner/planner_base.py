#!/usr/bin/env python
# -*- coding: utf-8 -*-
from abc import (ABCMeta, abstractmethod)
from py_matplanering.core.input import Input
from py_matplanering.core.schedule import Schedule

class PlannerBase(metaclass=ABCMeta):
    @abstractmethod
    def plan_init(self, inp: Input, options: dict) -> Schedule:
        pass

    @abstractmethod
    def plan_schedule(self, sch: Schedule):
        pass

