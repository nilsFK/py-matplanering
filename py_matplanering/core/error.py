#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Any

class BaseError(Exception):
    def __init__(self, message: Any):
        super(BaseError, self).__init__(message)
        self.message = message

class AppError(BaseError):
    """ Applied by implementing code. """
    def __init__(self, message: Any, capture_data: dict={}):
        super(AppError, self).__init__(message)
        self.capture_data = capture_data

    def __str__(self):
        return "An implementing app specific error occured: " + self.message
