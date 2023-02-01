#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, json
from pathlib import Path

from py_matplanering.utilities.common import (
    as_obj, as_dict, underscore_to_camelcase, camelcase_to_underscore
)
from py_matplanering.utilities.config import readConfig
from py_matplanering.core.automator_controller import AutomatorController
from py_matplanering.core.planner.planner_randomizer import PlannerRandomizer
from py_matplanering.core.planner.planner_food_menu import PlannerFoodMenu
from py_matplanering.utilities import loader

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
        Path(config_data['output_path']).write_text(json.dumps(schedule.as_dict()))
        print("OK!")
