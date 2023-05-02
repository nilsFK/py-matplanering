#!/usr/bin/env python
# -*- coding: utf-8 -*-

from configparser import ConfigParser as config_parser

def readConfig(config_path, section):
    config = config_parser()
    configs = config.read(config_path)
    if hasattr(config, 'items'):
        return dict(config.items(section))
    else:
        return dict(config[section])
