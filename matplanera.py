#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, json
from pathlib import Path
from py_matplanering.utilities.common import (
    as_obj, as_dict
)
from py_matplanering.core.automator_controller import AutomatorController

def make_schedule(args: dict) -> dict:
    raw_tagged_data = args['tagged_data']
    raw_rule_set = args['rule_set']
    automator_ctrl = AutomatorController()
    schedule = automator_ctrl.build(raw_tagged_data, raw_rule_set)
    if schedule is False:
        print("Failed to create schedule due to: %s" % (automator_ctrl.get_build_error('msg')))
    return schedule

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description='Process sources to produce a schedule.')
    argparser.add_argument('tagged_data_path',
        metavar='N',
        type=str,
        help='Source file from which tagged data will be extracted')
    argparser.add_argument('rule_set_path',
        metavar='N',
        type=str,
        help='Source file from which rule set will be extracted and applied to tagged data')
    argparser.add_argument('schedule_output_path',
        metavar='N',
        type=str,
        help='Source file to which final schedule will be written')
    args = argparser.parse_args()
    # Get output path
    schedule_output_path_str = args.schedule_output_path
    # Get tagged data
    tagged_data_str = Path(args.tagged_data_path).read_text()
    if len(tagged_data_str) == 0:
        raise Exception("tagged data source file is empty. Expected: JSON formatted data")
    tagged_data_dct = json.loads(tagged_data_str)
    print("Tagged data:", tagged_data_dct)

    # Get rule set
    rule_set_str = Path(args.rule_set_path).read_text()
    if len(rule_set_str) == 0:
        raise Exception("rule set source file is empty. Expected: JSON formatted data")
    rule_set_dct = json.loads(rule_set_str)
    print("Rule set:", rule_set_dct)
    schedule = make_schedule(dict(
        tagged_data=tagged_data_dct,
        rule_set=rule_set_dct
    ))
    if schedule is not False:
        print("Writing schedule to file...")
        Path(schedule_output_path_str).write_text(json.dumps(schedule.as_dict()))
        print("OK!")
