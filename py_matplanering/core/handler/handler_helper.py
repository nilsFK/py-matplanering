#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file should only contain functions intended
# for helping with handlers.

from typing import Any

def link_handler_chain(handlers: list) -> list:
    for idx, handler in enumerate(handlers):
        if idx < len(handlers)-1:
            next_handler = handlers[idx+1]
            handler.set_next(next_handler)
    return handlers

def run_handler_chain(handlers: list, request: Any):
    return handlers[0].handle(request)
