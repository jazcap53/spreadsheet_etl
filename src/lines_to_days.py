# file: lines_to_days.py
# andrew jarcho
# 2017-01-05

# python: 3.5


import datetime
from datetime import date
import re
import sys


class Event:
    """
    Each Event belongs to a Day, and is an item in that Day's list
    of Events.
    """
    def __init__(self, segment):
        if not len(segment) == 3:
            raise ValueError
        self.action = segment[0].strip()[0]
        self.mil_time = segment[1]
        self.hours = segment[2]

    def __str__(self):
        return 'action: {}, time: {}, hours: {:.2f}\n'.format(self.action,
                self.mil_time, self.hours)


class DayLabel:
    """
    A DayLabel consists of a day of the week, coupled with a
    datetime.date structure.
    """
    week = ('Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
            'Saturday')

    def __init__(self, weekday_indicator, dt_date):
        if not 0 <= weekday_indicator <= 6:
            raise ValueError
        self.weekday = DayLabel.week[weekday_indicator]
        self.dt_date = dt_date

    def __str__(self):
        return '{} {}-{:02}-{:02}'.format(self.weekday, self.dt_date.year,
                self.dt_date.month, self.dt_date.day)
    

class Day:
    """
    A Day consists of a DayLabel, and a list of Events.
    """
    def __init__(self, dt_date, wkday_ind):
        self.day_label = DayLabel(wkday_ind, dt_date)
        self.events = []

    def __str__(self):
        ret = '{}\n'.format(self.day_label.__str__())
        for item in self.events:
            ret += item.__str__()
        return ret

    def add_event(self, an_event):
        if not isinstance(an_event, Event):
            raise TypeError
        self.events.append(an_event)


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
        m = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', s)  # TODO: change to call to is_date()
        # group(3) is the year, group(1) is the month, group(2) is the day
        d = [int(m.group(x)) for x in (3, 1, 2)]
        d_obj = datetime.date(d[0], d[1], d[2])
        return d_obj


if __name__ == '__main__':
    filename = len(sys.argv) > 1 and sys.argv[1] or 'sheet_001.csv'
    with open(filename, 'r') as infile:
        l_t_d = LinesToDays(infile)
        l_t_d.read_lines()
