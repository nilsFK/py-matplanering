#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, json, copy, random
from pathlib import Path

from py_matplanering.automator_controller import AutomatorController
from py_matplanering.core.schedule.schedule import Schedule, ScheduleEvent
from py_matplanering.core.error import AppError
from py_matplanering.core.context import ScheduleEventFilterContext

from py_matplanering.utilities.common import (
    as_obj, as_dict, underscore_to_camelcase, camelcase_to_underscore
)
from py_matplanering.utilities.config import readConfig
from py_matplanering.utilities import time_helper, loader, schedule_helper, common, misc
from py_matplanering.utilities.logger import Logger, LoggerLevel

from tabulate import tabulate

from typing import List

def make_schedule(args: dict) -> dict:
    raw_event_data = args['event_data']
    raw_rule_set = args['rule_set']
    sch_interval = (args['schedule_startdate'], args['schedule_enddate'])
    planning_interval = None
    if args.get('planning_startdate') and args.get('planning_enddate'):
        planning_interval = (args['planning_startdate'], args['planning_enddate'])
    automator_ctrl = AutomatorController(sch_interval, sch_options=dict(
        include_props=['id', 'name', 'prio'],
        event_defaults=dict(
            prio=5000
        ),
        iter_method=args['iter_method'],
        planning_interval=planning_interval
    ), build_options=dict(
        iterations=args.get('iterations', 1),
        strategy=args.get('strategy', misc.BuildStrategy.IGNORE_PLACED_DAYS)
    ))
    planner = loader.build_planner(args['planner'])
    automator_ctrl.set_planner(planner)

    # Sanity check: create a custom event filter which returns all events to ensure
    # that custom schedule events works as intended
    def my_event_filter(ctx: ScheduleEventFilterContext) -> List[ScheduleEvent]:
        assert isinstance(ctx.get_date(), str)
        assert isinstance(ctx.get_schedule(), Schedule)
        assert isinstance(ctx.get_schedule_events(), list)
        return ctx.get_schedule_events()
    automator_ctrl.add_schedule_event_filter('my_event_filter', my_event_filter)
    # Add another to ensure multiple schedule event filters is OK.
    automator_ctrl.add_schedule_event_filter('my_event_filter_2', my_event_filter)

    if args.get('schedule'):
        automator_ctrl.init_schedule(args['schedule'])
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
            method = sch_event.get_metadata('method', 'unknown', scope='system')
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

def sample_schedule(schedule_dct: dict, n_percentage: int, n_min: int=1, d_keys: list=None):
    """ Samples a subset of schedule_dct and returns a new dict """
    if n_percentage > 100 or n_percentage < 0:
        raise Exception('n_percentage must range between 0-100, instead got: %s' % (n_percentage))
    if d_keys is None:
        d_keys = list(schedule_dct['days'])
    k = int((n_percentage/100)*len(d_keys))
    if n_min is not None and k < n_min:
        k = min(n_min, len(d_keys))
    sampled_d_keys = random.sample(d_keys, k)

    # clear events from days that are not sampled
    sampled_schedule_dct = copy.deepcopy(schedule_dct)
    for date in sampled_schedule_dct['days']:
        day = sampled_schedule_dct['days'][date]
        if date not in sampled_d_keys:
            day['events'] = []
    return sampled_schedule_dct

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='Process sources to produce a schedule.')
    argparser.add_argument('config_path',
        metavar='N',
        type=str,
        help='Path to config file containing further required schedule data')
    argparser.add_argument('--logger',
        metavar='',
        type=str,
        choices=['DEBUG', 'INFO', 'FATAL', 'OFF'],
        help="Logger option. Accepts one of the following strings: 'DEBUG', 'INFO', 'FATAL', 'OFF'.")
    args = argparser.parse_args()

    config_data = readConfig(args.config_path, 'Config')

    try:
        global_config_data = readConfig('config/global_config.ini', 'Global')
        Logger.log('Read global config', LoggerLevel.INFO)
    except Exception:
        global_config_data = None

    # Activate | Deactivate logger
    # ============================
    max_verbosity = None
    Logger.deactivate() # default
    if args.logger is not None and args.logger != 'OFF':
        Logger.activate()
        max_verbosity = LoggerLevel[args.logger]
    elif args.logger is None and global_config_data:
        logger_level = global_config_data['logger_level']
        if global_config_data['logger'] == 'on':
            Logger.activate()
            max_verbosity = LoggerLevel[logger_level]

    Logger.log('initializing', verbosity=LoggerLevel.INFO)

    # Get event data
    # ==============
    Logger.log('fetch event data', verbosity=LoggerLevel.INFO)
    event_data_str = Path(config_data['event_data_path']).read_text()
    if len(event_data_str) == 0:
        raise AppError("event data source file is empty. Expected: JSON formatted data")
    event_data_dct = json.loads(event_data_str)
    del event_data_str
    if config_data.get('filter_event_ids'):
        config_data['filter_event_ids'] = [int(id_) for id_ in config_data.get('filter_event_ids').split(',')]
        tmp_event_data_lst = []
        for event_row in event_data_dct['data']:
            if event_row['id'] not in config_data['filter_event_ids']:
                continue
            tmp_event_data_lst.append(event_row)
        event_data_dct['data'] = tmp_event_data_lst
        del tmp_event_data_lst
    # print("Event data:", event_data_dct)

    # Read schedule output file
    # =========================
    sampled_schedule_obj = None
    if config_data.get('init_schedule_path'):
        Logger.log('Initializing schedule from given path: %s' % (config_data['init_schedule_path']), verbosity=LoggerLevel.INFO)
        try:
            sampled_schedule_str = Path(config_data['init_schedule_path']).read_text()
            sampled_schedule_dct = json.loads(sampled_schedule_str)
            d_keys = None # use default: all dates in sampled_schedule_dct
            if config_data.get('sample_method') == 'require_placed_day':
                d_keys = []
                for date in sampled_schedule_dct['days']:
                    if len(sampled_schedule_dct['days'][date]['events']) > 0:
                        d_keys.append(date)
            sampled_schedule_dct = sample_schedule(sampled_schedule_dct,
                n_percentage=common.nvl_int(config_data.get('sample_size_percent')),
                n_min=common.nvl_int(config_data.get('sample_size_min')),
                d_keys=d_keys
            )
            del sampled_schedule_str
        except FileNotFoundError:
            sampled_schedule_dct = None
            Logger.log('File to init schedule path not found.', verbosity=LoggerLevel.INFO)
        if sampled_schedule_dct:
            # Convert sampled_schedule_dct: dict --> sampled_schedule_obj: Schedule
            sampled_schedule_obj = schedule_helper.parse_schedule(sampled_schedule_dct)
            sampled_schedule_obj.set_name('sampled_schedule')
            Logger.log('Reading pre-defined schedule with %s events' % (schedule_helper.count_placed_schedule_days(sampled_schedule_obj)), LoggerLevel.INFO)

    # Parse and get rule set file paths
    # =================================
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
    # =========================
    rule_sets = []
    for path in paths:
        Logger.log('Reading path: %s' % (path), verbosity=LoggerLevel.DEBUG)
        rule_set_str = Path(path).read_text()
        if len(rule_set_str) == 0:
            raise AppError("rule set source file is empty. Expected: JSON formatted data")
        rule_set_dct = json.loads(rule_set_str)
        rule_sets.append(rule_set_dct)

    # Create schedule with input arguments
    # ====================================
    Logger.log('Make schedule', verbosity=LoggerLevel.INFO)
    strategy = misc.BuildStrategy.IGNORE_PLACED_DAYS
    if config_data.get('strategy'):
        strategy = misc.BuildStrategy[config_data['strategy']]
    schedule = make_schedule(dict(
        event_data=event_data_dct,
        rule_set=rule_sets,
        schedule_startdate=config_data['schedule_startdate'],
        schedule_enddate=config_data['schedule_enddate'],
        planning_startdate=config_data.get('planning_startdate'),
        planning_enddate=config_data.get('planning_enddate'),
        planner=config_data['planner'],
        iter_method=config_data['iter_method'],
        schedule=sampled_schedule_obj,
        iterations=common.nvl_int(config_data['iterations']),
        strategy=strategy
    ))
    if schedule is False:
        Logger.log('Schedule is False', LoggerLevel.FATAL)
    if schedule is not False:
        try:
            sch_dct = schedule.as_dict()
            if sch_dct is None:
                raise AppError('Unexpected None returned by schedule.as_dict()')
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
                    raise AppError('Unknown group_table_by: %s (select from: %s)' % (config_data['group_table_by'], ['event', 'date']))
                if table and headers:
                    print(tabulate(table, headers, tablefmt=config_data.get('tablefmt', 'fancy_grid')))
            print("OK!")
        except Exception as exc:
            if Logger.is_activated():
                Logger.print(max_verbosity=max_verbosity)
            raise exc
    if Logger.is_activated():
        Logger.print_log(max_verbosity=max_verbosity)

    if schedule:
        print("Total planned events: %s / %s" % (len(schedule.get_events()), len(schedule.get_days())))

