# file: lines_to_days.py
# andrew jarcho
# 2017-01-05

# python: 2.7, 3.5


from __future__ import print_function

import datetime
from datetime import date
import re
import sys


def validate_segment(segment):
    """
    valid segments: 'b', 'time', ['float']
                    's', 'time', ['float']
                    'w', 'time', 'float'
    """
    if any(segment) and not segment[0] or \
            len(segment[0]) and segment[0][0] not in ('b', 's', 'w') or \
            len(segment[0]) and segment[0][0] == 'w' and not segment[2] or \
            segment[2] != '' and not re.match(r'[1,2]?\d\.\d{2}', segment[2]):
        return False
    return True


class Event:
    """
    Each Event belongs to a Day, and is an item in that Day's list
    of Events.
    """
    def __init__(self, segment):
        if not len(segment) == 3:
            raise ValueError('Bad segment length')
        if not validate_segment(segment):
            raise ValueError('Bad segment value')
        if any(segment):
            self.action = segment[0][0]
            self.mil_time = segment[1]
            self.hours = segment[2] if segment[2] else None
        else:
            self.action = None
            self.mil_time = None
            self.hours = None

    def __str__(self):
        ret = 'action: {}, time: {}'.format(self.action, self.mil_time)
        if self.hours:
            ret += ', hours: {:.2f}'.format(float(self.hours))
        return ret


class Day:
    """
    A Day consists of a datetime.date, and a list of Events.
    """
    def __init__(self, dt_date):
        self.dt_date = dt_date
        self.events = []

    def __str__(self):
        ret = '{}\n'.format(self.dt_date)
        for item in self.events:
            ret += item.__str__() + '\n'
        return ret

    def add_event(self, an_event):
        if not isinstance(an_event, Event):
            raise TypeError
        self.events.append(an_event)


class Week:
    """
    A Week is a list of seven Days, each beginning at 0:00 (midnight),
    with the first Day being a Sunday.
    """
    def __init__(self, dt_date):
        if dt_date.weekday() != 6:  # a Sunday, per datetime.date.weekday()
            raise ValueError
        self.day_list = [Day(dt_date + datetime.timedelta(days=x)) for x in range(7)]

    def __str__(self):
        ret = '\nWeek of Sunday, {}:\n'.format(self.day_list[0].dt_date)
        underscores = '=' * (len(ret) - 2)
        ret += underscores + '\n'
        for i in range(7):
            ret += '    ' + self.day_list[i].__str__()
        return ret


class ReadWeeks:
    """

    """
    my_weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

    def __init__(self, infile):
        self.infile = infile
        self.weeks = []
        self.sunday_date = None
        self.have_unstored_event = False
        self.new_week = None

    def read_lines(self):
        """
        Ignore header lines, which are non-blank lines with certain characteristics.
        Blank lines mean 'go to the next week'.
        """
        for line in self.infile:
            no_commas = line.strip().split(',')
            if self.is_header(no_commas):  # TODO: needs further definition
                continue
            if not any(no_commas):  # a blank line in spreadsheet
                self.reset_week()
                continue
            if not self.sunday_date:
                my_match = self.check_for_date(no_commas[0])
                if not my_match:
                    continue
                self.sunday_date = self.match_to_date_obj(my_match)
                self.new_week = Week(self.sunday_date)
            if any(no_commas[1:]):
                self.load_line(no_commas[1:])
        self.reset_week()  # save any unstored data
        for i in range(len(self.weeks)):
            print(self.weeks[i])

    def is_header(self, l):
        return l[1] == 'Sun'  # TODO: this is just a placeholder

    def reset_week(self):
        if self.sunday_date and self.new_week and self.have_unstored_event:
            self.weeks.append(self.new_week)
        self.sunday_date = None
        self.new_week = None
        self.have_unstored_event = False

    def check_for_date(self, s):
        m = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', s)
        return m if m else None

    def match_to_date_obj(self, m):
        # group(3) is the year, group(1) is the month, group(2) is the day
        d = [int(m.group(x)) for x in (3, 1, 2)]
        d_obj = datetime.date(d[0], d[1], d[2])
        return d_obj

    def load_line(self, line):
        for ix in range(7):
            a_event = Event(line[3*ix: 3*ix + 3])
            if a_event.action:
                self.new_week.day_list[ix].add_event(a_event)
                self.have_unstored_event = True

    def to_my_day(self, ix):
        return self.my_weekdays[ix]


if __name__ == '__main__':
    filename = len(sys.argv) > 1 and sys.argv[1] or 'sheet_001.csv'
    with open(filename, 'r') as infile:
        r_w = ReadWeeks(infile)
        r_w.read_lines()
