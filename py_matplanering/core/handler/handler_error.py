#!/usr/bin/env python
# -*- coding: utf-8 -*-
from py_matplanering.core.error import BaseError

class HandlerError(BaseError):
    def __init__(self, message, capture_data = {}):
        super(HandlerError, self).__init__(message)
        self.capture_data = capture_data

    def __str__(self):
        return self.message
