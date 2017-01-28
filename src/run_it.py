# file: run_it.py
# andrew jarcho
# 2017-01-21


import sys
import read_funs
from lines_to_days import Read, Purge
from spreadsheet_etl.tests.file_access_wrappers import FileReadAccessWrapper


weeks = []

if __name__ == '__main__':
    # r = Read(weeks, FileReadAccessWrapper(sys.argv[1]))
    infile = read_funs.open_file(FileReadAccessWrapper(sys.argv[1]))
    # r.open_file()
    weeks = read_funs.read_lines(infile, weeks)
    # print(r)
    read_funs.print_out(weeks)
    p = Purge(weeks)
    p.purge()
    print(p)
