# file: run_it.py
# andrew jarcho
# 2017-01-21


import sys
from lines_to_days import ReadAndPurge
from spreadsheet_etl.tests.file_access_wrappers import FileReadAccessWrapper


if __name__ == '__main__':
    r_a_p = ReadAndPurge(FileReadAccessWrapper(sys.argv[1]))
    r = r_a_p.createRead()
    r.read_lines()
    # print(r_a_p)
    print(r)
    p = r_a_p.createPurge()
    p.purge()
    # print(r_a_p)
    print(p)
