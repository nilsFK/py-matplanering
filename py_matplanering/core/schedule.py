#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Schedule:
    def __init__(self):
        self.schedule = dict(
            default=True,
            built=False
        )

    def as_dict(self) -> dict:
        return self.schedule