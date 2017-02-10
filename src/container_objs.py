# file: src/container_objs.py
# andrew jarcho
# 2017-01-21

# python: 2.7, 3.5, 3.6


from __future__ import print_function

import datetime
import re
import sys
from collections import namedtuple


def validate_segment(segment):
    """
    valid segments: 'b', 'time'[, 'float']
                    's', 'time'
                    'w', 'time', 'float'
    """
    if not any(segment) or \
            any(segment) and (not segment[0] or not segment[1]) or \
            len(segment[0]) and segment[0][0] not in ('b', 's', 'w') or \
            len(segment[0]) and segment[0][0] == 's' and segment[2] or \
            len(segment[0]) and segment[0][0] == 'w' and not segment[2] or \
            segment[2] != '' and not re.match(r'[1,2]?\d\.\d{2}', segment[2]):
        return False
    return True


class Event(namedtuple('Event', 'action, mil_time, hours')):
    __slots__ = ()
    def __init__(self, a, m, h):
        if not validate_segment([a, m, h]):
            raise ValueError


class Day(namedtuple('Day', 'dt_date, events')):
    __slots__ = ()
    def __init__(self, d, e):
        if not isinstance(d, datetime.date):
            raise TypeError


class Week(namedtuple('Week',
        'Sunday, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday')):
    __slots__ = ()
    def __init__(self, su, mo, tu, we, th, fr, sa):
        param_list = [su, mo, tu, we, th, fr, sa]
        for ix, p in enumerate(param_list):
            if not isinstance(p, Day):
                raise TypeError
            elif not ix and p.dt_date.weekday() != 6:
                raise ValueError

weeks = []


# Code below this line is normally called in debug mode only.
#==============================================================================

def print_event(e, out):
    out_str = 'action: {}, time: {}'.format(e.action, e.mil_time)
    if e.hours:
        out_str += ', hours: {:.2f}'.format(float(e.hours))
    out.write(out_str + u'\n')


def print_day(d, out):
    out.write('{}\n'.format(d.dt_date))
    for item in d.events:
        print_event(item, out)


def print_week(w, out):
    header = '\nWeek of Sunday, {}:\n'.format(w[0].dt_date)
    underscores = '=' * (len(header) - 2) + '\n'
    out.write(header + underscores)
    for d in w:
        out.write('    ')
        print_day(d, out)
    print()
