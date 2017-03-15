#!/usr/bin/python3.5


# file: src/extract/run_it.py
# andrew jarcho
# 2017-01-21


"""
Run the extract phase of the pipeline.

read_fns() reads raw data from the spreadsheet, and groups it by day and week.
purge_fns() removes days for which the data are incomplete.
"""

from __future__ import print_function

import sys
import read_fns
import purge_fns
import container_objs
from container_objs import weeks
from spreadsheet_etl.tests.file_access_wrappers import FileReadAccessWrapper


def print_out(weeks):
    for week in weeks:
        container_objs.print_week(week, out=sys.stdout)
    print()

if __name__ == '__main__':
    infile = read_fns.open_file(FileReadAccessWrapper(sys.argv[1]))
    weeks = read_fns.read_lines(infile, weeks)
    weeks = purge_fns.purge(weeks)
    print_out(weeks)
