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

from tabulate import tabulate

def make_schedule(args: dict) -> dict:
    raw_event_data = args['event_data']
    raw_rule_set = args['rule_set']
    automator_ctrl = AutomatorController(args['startdate'], args['enddate'], dict(
        include_props=['id', 'name']
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
    headers = ['Date', 'Week', 'Day', 'Item', 'Boundaries', 'Method', 'Quota']
    days = sch.get_days()
    table = []
    for date in days:
        row = []
        row.append(date)
        row.append(time_helper.get_week_number(time_helper.parse_date(date)))
        row.append(time_helper.get_weekday_name(time_helper.parse_date(date)))
        for sch_event in sch.get_events_by_date(date):
            row2 = copy.copy(row)
            row2.append(sch_event.get_name())
            # Add boundaries
            boundaries = sch_event.get_boundaries()
            printable_boundaries = []
            for boundary in boundaries:
                printable_boundaries.append(type(boundary).__name__)
            row2.append(", ".join(printable_boundaries))
            row2.append(sch_event.get_metadata('method'))
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

    # Get event data
    event_data_str = Path(config_data['event_data_path']).read_text()
    if len(event_data_str) == 0:
        raise Exception("event data source file is empty. Expected: JSON formatted data")
    event_data_dct = json.loads(event_data_str)
    print("Event data:", event_data_dct)

    # Get rule set
    rule_set_str = Path(config_data['rule_set_path']).read_text()
    if len(rule_set_str) == 0:
        raise Exception("rule set source file is empty. Expected: JSON formatted data")
    rule_set_dct = json.loads(rule_set_str)
    print("Rule set:", rule_set_dct)

    # Create schedule with input arguments
    schedule = make_schedule(dict(
        event_data=event_data_dct,
        rule_set=rule_set_dct,
        startdate=config_data['startdate'],
        enddate=config_data['enddate'],
        planner=config_data['planner']
    ))
    if schedule is not False:
        sch_dct = schedule.as_dict()
        if sch_dct is None:
            raise Exception('Unexpected None returned by schedule.as_dict()')
        Path(config_data['output_path']).write_text(json.dumps(sch_dct))
        # Output in tabulate form
        if config_data['group_table_by'] == 'event':
            table, headers = make_event_table(schedule)
        elif config_data['group_table_by'] == 'date':
            table, headers = make_date_table(schedule)
        print(tabulate(table, headers, tablefmt=config_data.get('tablefmt', 'fancy_grid')))
        print("Total planned events:", len(schedule.get_events()))
        print("OK!")
