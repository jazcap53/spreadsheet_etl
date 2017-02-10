# file: src/run_it.py
# andrew jarcho
# 2017-01-21

# python: 2.7, 3.5, 3.6


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
    if __debug__:
        print_out(weeks)
    weeks = purge_fns.purge(weeks)
    if __debug__:
        print_out(weeks)
