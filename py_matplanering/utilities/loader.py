#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
import importlib
import os, os.path
from py_matplanering.utilities import common

def __load_module(module_name, module_folder: str):
    safe_module_name = common.path_leaf(module_name)
    if not safe_module_name.startswith("py_matplanering.core.%s" % module_folder):
        safe_module_name.replace(".", "")
        safe_module_name = "%s.%s" % (module_folder, safe_module_name)
    print("Load module:", safe_module_name)
    safe_module = importlib.import_module("%s" % safe_module_name)
    return safe_module

def __load_modules(module_names: list, module_folder) -> dict:
    rs = {}
    for module_name in module_names:
        safe_module = __load_module(module_name, module_folder)
        rs[module_name] = safe_module
    return rs

def load_boundaries(boundaries: list) -> dict:
    rs = __load_modules(boundaries, "py_matplanering.core.boundary")
    return rs
