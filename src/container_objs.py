# file: container_objs.py
# andrew jarcho
# 2017-01-21

# python: 2.7, 3.5


from __future__ import print_function

import datetime
from datetime import date
import re
import sys


def validate_segment(segment):
    """
    valid segments: 'b', 'time'[, 'float']
                    's', 'time'
                    'w', 'time', 'float'
    """
    if any(segment) and (not segment[0] or not segment[1]) or \
            len(segment[0]) and segment[0][0] not in ('b', 's', 'w') or \
            len(segment[0]) and segment[0][0] == 's' and segment[2] or \
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
        self.day_list = [Day(dt_date + datetime.timedelta(days=x))
                for x in range(7)]

    def __str__(self):
        ret = '\nWeek of Sunday, {}:\n'.format(self.day_list[0].dt_date)
        underscores = '=' * (len(ret) - 2)
        ret += underscores + '\n'
        for i in range(7):
            ret += '    ' + self.day_list[i].__str__()
        return ret