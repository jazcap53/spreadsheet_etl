# file: run_it.py
# andrew jarcho
# 2017-01-21


import sys
from lines_to_days import Read, Purge
from spreadsheet_etl.tests.file_access_wrappers import FileReadAccessWrapper


weeks = []

if __name__ == '__main__':
    r = Read(weeks, FileReadAccessWrapper(sys.argv[1]))
    r.open_file()
    r.read_lines()
    print(r)
    p = Purge(weeks)
    p.purge()
    print(p)
