# file: run_it.py
# andrew jarcho
# 2017-01-21


import sys
import read_fns
import purge_fns
# from lines_to_days import Read, Purge
from spreadsheet_etl.tests.file_access_wrappers import FileReadAccessWrapper


weeks = []

def print_out(weeks):
    for week in weeks:
        print(week)
    print()

if __name__ == '__main__':
    infile = read_fns.open_file(FileReadAccessWrapper(sys.argv[1]))
    weeks = read_fns.read_lines(infile, weeks)
    print_out(weeks)
    weeks = purge_fns.purge(weeks)
    print_out(weeks)
    # p = Purge(weeks)
    # p.purge()
    # print(p)
