#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, json, copy
from pathlib import Path

from py_matplanering.utilities.common import (
    as_obj, as_dict, underscore_to_camelcase, camelcase_to_underscore
)
from py_matplanering.utilities.config import readConfig
from py_matplanering.utilities import time_helper
from py_matplanering.core.automator_controller import AutomatorController
from py_matplanering.core.planner.planner_randomizer import PlannerRandomizer
from py_matplanering.core.planner.planner_food_menu import PlannerFoodMenu
from py_matplanering.core.schedule.schedule import Schedule
from py_matplanering.utilities import loader
from py_matplanering.utilities.logger import Logger, LoggerLevel

from tabulate import tabulate

def make_schedule(args: dict) -> dict:
    raw_event_data = args['event_data']
    raw_rule_set = args['rule_set']
    automator_ctrl = AutomatorController(args['startdate'], args['enddate'], sch_options=dict(
        include_props=['id', 'name'],
        event_defaults=dict(
            prio=5000
        ),
        iter_method=args['iter_method']
    ))
    planner_name = args['planner']
    if '_' not in planner_name: # assume camel case
        planner_name_cc = planner_name
        planner_name_us = camelcase_to_underscore(planner_name)
    else: # assume underscore
        planner_name_us = planner_name
        planner_name_cc = underscore_to_camelcase(planner_name)

    planner_module = loader.load_planner(planner_name_us)
    planner = getattr(planner_module, planner_name_cc)()
    automator_ctrl.set_planner(planner)
    schedule = automator_ctrl.build(raw_event_data, raw_rule_set)
    if schedule is False:
        print("Failed to create schedule due to: %s" % (automator_ctrl.get_build_error('msg')))
    return schedule

def make_event_table(sch: Schedule) -> tuple:
    headers = ['Event', 'Id', 'Planned', 'Dates']
    table = []
    days = sch.get_days()
    event_data = {}
    for date in days:
        for sch_event in sch.get_events_by_date(date):
            if sch_event.get_id() not in event_data:
                event_data[sch_event.get_id()] = dict(
                    dates=[],
                    name=sch_event.get_name(),
                    occurrences=0
                )
            event_data[sch_event.get_id()]['dates'].append(date)
            event_data[sch_event.get_id()]['occurrences'] += 1
            # Add boundaries
            boundaries = sch_event.get_boundaries()
            printable_boundaries = []
            for boundary in boundaries:
                printable_boundaries.append(type(boundary).__name__)
            event_data[sch_event.get_id()]['printable_boundaries'] = printable_boundaries
    total_occurrences = 0
    for event_id in list(event_data):
        event_row = event_data[event_id]
        row = []
        row.append(event_row['name'])
        row.append(event_id)
        row.append(event_row['occurrences'])
        date_str = ''
        for date in event_row['dates']:
            date_str += "{date} ({week_day})\n".format(**{
                'date': date,
                'week_day': time_helper.get_weekday_name(date, short=True, to_lower=True)
            })
        date_str = date_str.strip("\n")
        row.append(date_str)
        table.append(row)
        total_occurrences += event_row['occurrences']
    table.append(['Total', None, total_occurrences])
    return table, headers

def make_date_table(sch: Schedule) -> tuple:
    headers = ['Date', 'Week', 'Day', 'Item', 'Id', 'Boundaries', 'Method', 'Quota']
    days = sch.get_days()
    table = []
    for date in days:
        row = []
        row.append(date)
        row.append(time_helper.get_week_number(time_helper.parse_date(date)))
        row.append(time_helper.get_weekday_name(time_helper.parse_date(date)))
        sch_events = sch.get_events_by_date(date)
        if len(sch_events) == 0:
            # fill remaining rows with empty strings
            for x in range(len(headers)-len(row)):
                row.append('')
            table.append(row)
            continue
        for sch_event in sch_events:
            row2 = copy.copy(row)
            row2.append(sch_event.get_name())
            row2.append(sch_event.get_id())
            # Add boundaries
            boundaries = sch_event.get_boundaries()
            printable_boundaries = []
            for boundary in boundaries:
                printable_boundaries.append(type(boundary).__name__)
            row2.append(", ".join(printable_boundaries))
            method = sch_event.get_metadata('method')
            method_str = ''
            for item in method:
                method_str += "{item}\n".format(**{
                    'item': item
                })
            row2.append(method_str)
            quota_str = ''
            for quota in sch.get_quotas(sch_event.get_id()):
                quota_str += "cap({min},{max}) ({time_unit}): used={used}/{quota}\n".format(**{
                    'min': quota['min'],
                    'max': quota['max'],
                    'time_unit': quota['time_unit'][:4],
                    'left': quota['quota']-quota['used'],
                    'used': quota['used'],
                    'quota': quota['max']-quota['min']+1
                })
            quota_str = quota_str.strip("|")
            row2.append(quota_str)
            table.append(row2)
    return table, headers

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='Process sources to produce a schedule.')
    argparser.add_argument('config_path',
        metavar='N',
        type=str,
        help='Path to config file containing further required schedule data')
    args = argparser.parse_args()

    config_data = readConfig(args.config_path, 'Config')

    global_config_data = readConfig('config/global_config.ini', 'Global')
    logger_level = global_config_data['logger_level']
    max_verbosity = LoggerLevel[logger_level]
    if global_config_data['logger'] == 'on':
        Logger.activate()
    Logger.log('initializing', verbosity=LoggerLevel.INFO)
    # Get event data
    Logger.log('fetch event data', verbosity=LoggerLevel.INFO)
    event_data_str = Path(config_data['event_data_path']).read_text()
    if len(event_data_str) == 0:
        raise Exception("event data source file is empty. Expected: JSON formatted data")
    event_data_dct = json.loads(event_data_str)
    print("Event data:", event_data_dct)

    # Parse and get file paths
    Logger.log('fetch rule set data', verbosity=LoggerLevel.INFO)
    paths_str = config_data['rule_set_path']
    paths = paths_str.split(",")
    if len(paths) == 1:
        paths = paths[0].split()
    tmp_paths = []
    for path_str in paths:
        path_str = path_str.strip()
        for quote in ['"', "'"]:
            if path_str.startswith(quote):
                path_str = path_str[1:-1]
        tmp_paths.append(path_str)
    paths = tmp_paths
    del tmp_paths

    # Load files into rule sets
    rule_sets = []
    for path in paths:
        Logger.log('Reading path: %s' % (path), verbosity=LoggerLevel.DEBUG)
        rule_set_str = Path(path).read_text()
        if len(rule_set_str) == 0:
            raise Exception("rule set source file is empty. Expected: JSON formatted data")
        rule_set_dct = json.loads(rule_set_str)
        rule_sets.append(rule_set_dct)

    # Create schedule with input arguments
    Logger.log('Make schedule', verbosity=LoggerLevel.INFO)
    schedule = make_schedule(dict(
        event_data=event_data_dct,
        rule_set=rule_sets,
        startdate=config_data['startdate'],
        enddate=config_data['enddate'],
        planner=config_data['planner'],
        iter_method=config_data['iter_method']
    ))
    try:
        if schedule is False:
            Logger.log('Schedule is False', LoggerLevel.FATAL)
        if schedule is not False:
            sch_dct = schedule.as_dict()
            if sch_dct is None:
                raise Exception('Unexpected None returned by schedule.as_dict()')
            Logger.log('Writing schedule to: %s' % (config_data['output_path']), LoggerLevel.INFO)
            Path(config_data['output_path']).write_text(json.dumps(sch_dct))
            # Output in tabulate form
            if config_data.get('group_table_by'):
                table, headers = None, None
                if config_data['group_table_by'] == 'event':
                    table, headers = make_event_table(schedule)
                elif config_data['group_table_by'] == 'date':
                    table, headers = make_date_table(schedule)
                else:
                    raise Exception('Unknown group_table_by: %s (select from: %s)' % (config_data['group_table_by'], ['event', 'date']))
                if table and headers:
                    print(tabulate(table, headers, tablefmt=config_data.get('tablefmt', 'fancy_grid')))
            print("OK!")
    finally:
        Logger.print(max_verbosity=max_verbosity)
    if schedule:
        print("Total planned events: %s / %s" % (len(schedule.get_events()), len(schedule.get_days())))
