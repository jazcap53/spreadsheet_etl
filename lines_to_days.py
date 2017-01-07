# file: lines_to_days.py
# andrew jarcho
# 2017-01-05

# python: 3.5


import datetime
import re
import sys


class LinesToDays:
    def __init__(self, infile):
        self.infile = infile
        self.days = []
        self.sunday_date = None
        self.today_offset = 0

    def convert(self):
        pass

    def read_lines(self):
        for line in self.infile:
            no_commas = line.split(',')
            if not any(no_commas):
                continue
            if self.is_date(no_commas[0]):
                self.sunday_date = self.date_str_to_obj(no_commas[0])
                print(str(self.sunday_date))  # TODO: debug line

    def is_date(self, s):
        m = re.match(r'\d{1,2}/\d{1,2}/\d{4}', s)
        return m

    def date_str_to_obj(self, s):
        m = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', s)
        # group(3) is the year, group(1) is the month, group(2) is the day
        d = [int(m.group(x)) for x in (3, 1, 2)]
        d_obj = datetime.date(d[0], d[1], d[2])
        return d_obj


if __name__ == '__main__':
    filename = len(sys.argv) > 1 and sys.argv[1] or 'sheet_001.csv'
    with open(filename, 'r') as infile:
        l_t_d = LinesToDays(infile)
        l_t_d.read_lines()
