#!/usr/bin/env python
# -*- coding: utf-8 -*-
from py_matplanering.utilities import common, time_helper

import inspect, os

from enum import Enum, unique

logger__log = []
logger__settings = dict(on=False)

@unique
class LoggerLevel(Enum):
    FATAL = 0
    DEBUG = 1
    INFO = 2

class Logger(metaclass=common.Singleton):
    @staticmethod
    def activate():
        logger__settings['on'] = True

    @staticmethod
    def deactivate():
        logger__settings['on'] = False

    @staticmethod
    def is_activated() -> bool:
        return logger__settings['on']

    @staticmethod
    def log(msg: str='', verbosity: LoggerLevel=None) -> bool:
        if verbosity is None:
            members = []
            for name, member in LoggerLevel.__members__.items():
                members.append(name)
            raise Exception('Verbosity is None, choose verbosity from LoggerLevel.[%s]' % (", ".join(members)))
        if not logger__settings['on']:
            return False
        if verbosity.value > 2 or verbosity.value < 0:
            raise Exception('Verbosity must be an integer from {0,1,2}. Got: %s' % (verbosity))
        frame = inspect.stack()[1]
        module = inspect.getmodule(frame[0])
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        dt_str = time_helper.time_now()
        logger__log.append(dict(
            msg=msg,
            full_date=dt_str,
            date=dt_str[0:10],
            time=dt_str[11:],
            filename=os.path.basename(frame.filename),
            full_path=frame.filename,
            verbosity=verbosity,
            method=calframe[1][3]
        ))
        return True

    @staticmethod
    def get_log(max_verbosity: LoggerLevel=None):
        if verbosity is None:
            return logger__log
        return [entry for entry in logger__log if entry['verbosity'] <= max_verbosity.value]

    @staticmethod
    def print(format_=None, max_verbosity: LoggerLevel=None):
        if format_:
            raise NotImplementedError
        for entry in logger__log:
            if max_verbosity is None or entry['verbosity'].value <= max_verbosity.value:
                print("%s:%s (%s): %s - %s" % (
                    entry['filename'],
                    entry['method'],
                    entry['time'],
                    entry['verbosity'].name,
                    entry['msg']
                ))
