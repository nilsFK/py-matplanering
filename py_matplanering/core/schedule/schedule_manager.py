#!/usr/bin/env python
# -*- coding: utf-8 -*-

from py_matplanering.core.schedule.schedule import Schedule
from py_matplanering.core.schedule.schedule import ScheduleEvent
from py_matplanering.core.error import BaseError

from typing import Any

import copy

class ScheduleManagerError(BaseError):
    def __init__(self, message, capture_data = {}):
        super(ScheduleManagerError, self).__init__(message)
        self.capture_data = capture_data

    def __str__(self):
        return self.message

class ScheduleManager:
    """ ScheduleManager is a collection of schedules which
    can be managed together to solicit a particular behavior
    when manipulating events; such as adding the event to one
    schedule and simultaneously removing it from all other schedules
    to make sure that the event is unique within the domain of the
    managed schedules, in contrast to being globally unique.
    One and only one schedule can be set to master which combined
    with tracking events will add events to master and remove from
    minions. Master schedule is not mandatory; all schedules could
    be minions but tracking (as just described) is not available with such a setup.
    Example:
    master_sch = Schedule(...)
    master_sch.add_event(...)
    sm = ScheduleManager()
    sm.add_master_schedule(master_sch)
    sm.spawn_minion_schedule('minion_1')
    sm.add_master_event([...], remove_from_minions=False)
    <do some work>
    sm.add_master_event([...], remove_from_minions=True)
    events = sm.get_master_schedule().get_events()
    <do something with events>
    """
    def __init__(self):
        self.schedules = {}
        self.master = None

    def __add_schedule(self, schedule: Schedule, sch_key: str=None, is_master: bool=False):
        if sch_key is None:
            raise ScheduleManagerError('key must be valid string (None is not a possible value)')
        if sch_key in self.schedules:
            raise ScheduleManagerError('sch_key: %s is already defined' % (sch_key))
        if len(sch_key) == 0:
            raise ScheduleManagerError('sch_key must be a non zero length string')
        schedule.set_name(sch_key)
        self.schedules[sch_key] = schedule
        if is_master:
            if self.master:
                raise ScheduleManagerError('Master is already set')
            if sch_key is None:
                sch_key = 'master'
            self.master = sch_key

    def __remove_schedule(self, sch_key: str=None):
        if sch_key is None:
            raise ScheduleManagerError('key must be valid string (None is not a possible value)')
        if sch_key not in self.schedules:
            raise ScheduleManagerError('sch_key: %s is undefined' % (sch_key))
        if len(sch_key) == 0:
            raise ScheduleManagerError('sch_key must be a non zero length string')
        if sch_key == 'master':
            raise ScheduleManagerError('Attempt to remove master schedule is not allowed.')
        del self.schedules[sch_key]

    def has_master_schedule(self):
        return self.master is not None

    def add_master_schedule(self, schedule: Schedule):
        self.__add_schedule(schedule, sch_key='master', is_master=True)

    def _add_minion_schedule(self, schedule: Schedule, sch_key: str):
        self.__add_schedule(schedule, sch_key, is_master=False)

    def spawn_minion_schedule(self, sch_key: str) -> Schedule:
        """ Copies the master as it is and becomes a minion. """
        minion = copy.deepcopy(self.get_master_schedule())
        self._add_minion_schedule(minion, sch_key)
        return self.schedules[sch_key]

    def despawn_minion_schedule(self, sch_key: str):
        self.__remove_schedule(sch_key)

    def set_master(self, master_sch_key: str):
        self.master = master_sch_key

    def __get_schedule(self, sch_key: str=None) -> Any:
        if key is None:
            return self.schedules
        return self.schedules[sch_key]

    def get_master_schedule(self) -> Schedule:
        return self.schedules['master']

    def get_minion_schedule(self, sch_key: str) -> Schedule:
        return self.schedules[sch_key]

    def __add_event(self, sch_key: str, date_list: list, sch_event: ScheduleEvent, remove_from_minions: bool=False):
        if len(list(self.schedules)) == 0:
            raise ScheduleManagerError('No schedules has been added. Add schedules using the add_schedule method')
        if sch_key not in self.schedules:
            raise ScheduleManagerError('Unknown sch_key %s provided. choose from: %s' % (sch_key, list(self.schedules)))
        self.schedules[sch_key].add_event(date_list, sch_event)
        if self.master and remove_from_minions:
            for other_sch_key in self.schedules:
                if other_sch_key == sch_key:
                    continue
                self.schedules[other_sch_key].remove_event(sch_event)

    def add_master_event(self, date_list: list, sch_event: ScheduleEvent, remove_from_minions: bool=False):
        if self.master is None:
            raise ScheduleManagerError('No master schedule has been specified')
        self.__add_event(self.master, date_list, sch_event, remove_from_minions)

    def add_minion_event(self, sch_key: str, date_list: list, sch_event: ScheduleEvent):
        self.__add_event(sch_key, date_list, sch_event)
