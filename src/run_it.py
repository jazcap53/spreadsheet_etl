# file: run_it.py
# andrew jarcho
# 2017-01-21


import sys
from lines_to_days import ReadAndPurge

if __name__ == '__main__':
    r_a_p = ReadAndPurge()
    r = r_a_p.Read()
    r.read_lines()
    print(r_a_p)
    p = r_a_p.Purge()
    p.purge()
    print(r_a_p)
