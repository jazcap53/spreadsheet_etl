# file: src/extract/container_objs.py
# andrew jarcho
# 2017-01-21

# python: 3.5


import datetime
import re
from collections import namedtuple


def validate_segment(segment):
    """
    valid segments: 'b', time, ''
                    'b', time, str(float)
                    's', time, ''
                    'w', time, str(float)
    """
    if not any(segment) or \
            any(segment) and (not segment[0] or not segment[1]) or \
            not re.match(r'[012]?\d:\d{2}', segment[1]) or \
            len(segment[0]) and segment[0][0] not in ('b', 's', 'w') or \
            len(segment[0]) and segment[0][0] == 's' and segment[2] or \
            len(segment[0]) and segment[0][0] == 'w' and not segment[2] or \
            segment[2] != '' and not re.match(r'[12]?\d\.\d{2}', segment[2]):
        return False
    return True


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


# TODO: is not calling super() for these 3 classes a problem?

class Event(namedtuple('EventTuple', 'action, mil_time, hours')):
    """
    Each EventTuple holds:
        action -- a character from the set {'b', 's', 'w'}
        mil_time -- a 24-hour time string as 'H:MM' or 'HH:MM'
        hours -- an interval expressed as str(float))
                 The interval may have one or two digits before
                 the decimal point, and will have exactly two digits
                 after. Its value may not be zero (0.00), but may be
                 the empty string.
    """
    __slots__ = ()  # prevents creation of per-instance dictionaries

    def __init__(self, a, m, h):
        """ Ctor used just to filter input """
        if not validate_segment([a, m, h]):
            raise ValueError('Event ctor called with invalid segment')


class Day(namedtuple('DayTuple', 'dt_date, events')):
    """
    Each DayTuple holds a datetime.date and a (possibly empty)
    list of Events
    """
    __slots__ = ()  # prevents creation of per-instance dictionaries

    def __init__(self, d, e):
        """ Ctor used just to filter input """
        if not isinstance(d, datetime.date):
            raise TypeError('Day ctor called with non-date first arg')
        if not isinstance(e, list):
            raise TypeError('Day ctor called with non-list second arg')


class Week(namedtuple('WeekTuple',
                      'Sunday, Monday, Tuesday, Wednesday, Thursday, Friday,'
                      ' Saturday')):
    """ Each WeekTuple holds seven named Day tuples """
    __slots__ = ()  # prevents creation of per-instance dictionaries

    def __init__(self, su, mo, tu, we, th, fr, sa):
        """ Ctor used just to filter input """
        param_list = [su, mo, tu, we, th, fr, sa]
        for ix, p in enumerate(param_list):
            if not isinstance(p, Day):
                raise TypeError('Week ctor with non-Day in param list')
            if not ix and p.dt_date.weekday() != 6:
                raise ValueError('Week ctor called with non-Sunday start'
                                 'date')

weeks = []
