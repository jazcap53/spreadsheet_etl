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


class ReadWeeks:
    """
    Read data from stream into Weeks, Days, and Events.
    """
    def __init__(self, infile):
        self.infile = infile
        self.weeks = []
        self.sunday_date = None  # the first day of each Week is a Sunday
        self.have_unstored_event = False
        self.new_week = None

    def __str__(self):
        ret = ''
        for i in range(len(self.weeks)):
            ret += self.weeks[i].__str__() + '\n'
        return ret

    def read_lines(self):
        """
        Skip header lines.
        Read and store Events a Week at a time.
        One or more blank lines mean 'this Week has ended'.
        """
        for line in self.infile:
            line = line.strip().split(',')
            if self.is_header(line):
                continue
            if not any(line):  # we had a blank row in the spreadsheet
                self.store_week()
                self.reset_week()
                continue
            if not self.sunday_date:
                found_match = self.check_for_date(line[0])
                if not found_match:  # we are not at the start of a week
                    continue
                self.sunday_date = self.match_to_date_obj(found_match)
                self.new_week = Week(self.sunday_date)
            if any(line[1:]):
                self.load_line(line[1:])
        self.store_week()  # saves any left-over unstored data
        self.reset_week()  # for consistency

    def is_header(self, l):
        return l[1] == 'Sun'

    def store_week(self):
        if self.sunday_date and self.new_week and self.have_unstored_event:
            self.weeks.append(self.new_week)

    def reset_week(self):
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

    def week_is_empty(self, week_ix):
        return all([self.day_is_empty(week_ix, d) for d in range(7)])

    def day_is_empty(self, week_ix, day_ix):
        return not len(self.weeks[week_ix].day_list[day_ix].events)

    def event_is_extra(self, event):
        return event.action != 'b'

    def restarts_purge(self, event):
        return event.action == 'b' and (not event.mil_time or not event.hours)

    def stops_purge(self, event):
        return event.action == 'b' and event.mil_time and event.hours

    def purge(self):
        purging = True
        week_ix, day_ix, event_ix, event = self.get_final_event()
        while event:  # event is None if there is no final event
            if purging:
                if self.stops_purge(event):
                    purging = False
                else:
                    print('popping {}'.format(event))
                    self.weeks[week_ix].day_list[day_ix].events.pop(event_ix)
            else:
                if self.restarts_purge(event):
                    purging = True
                else:
                    print('keeping {}'.format(event))
            week_ix, day_ix, event_ix, event = self.get_previous_event(week_ix, day_ix, event_ix)

    def get_final_event(self):
        week_ix = self.get_final_nonempty_week()
        if week_ix is not None:
            day_ix = self.get_final_nonempty_day(week_ix)
            event_ix = len(self.weeks[week_ix].day_list[day_ix].events) - 1
            event = self.weeks[week_ix].day_list[day_ix].events[event_ix]
            return (week_ix, day_ix, event_ix, event)
        return (None, None, None, None)

    def get_previous_event(self, week_ix, day_ix, event_ix):
        """
        pre: week_ix, day_ix, event_ix are not None
        """
        if event_ix:
            event_ix -= 1
            event = self.weeks[week_ix].day_list[day_ix].events[event_ix]
        else:
            week_ix, day_ix = self.get_previous_nonempty_day(week_ix, day_ix)
            if week_ix is not None:  # there was a previous nonempty day
                event_ix = len(self.weeks[week_ix].day_list[day_ix].events) - 1
                print('week: {}, day: {}, event: {}'.format(week_ix, day_ix, event_ix))
                event = self.weeks[week_ix].day_list[day_ix].events[event_ix]
            else:
                return (None, None, None, None)
        if week_ix is not None:
            return (week_ix, day_ix, event_ix, event)
        return (None, None, None, None)

    def get_final_nonempty_week(self):
        week_ix = len(self.weeks) - 1
        while week_ix > -1 and self.week_is_empty(week_ix):
            week_ix -= 1
        return None if week_ix == -1 else week_ix

    def get_final_nonempty_day(self, week_ix):
        """
        param: week_ix is a non-None return value from self.get_final_nonempty_week()
        returns: integer between 0 and 6 inclusive
        """
        day_ix = 6
        while day_ix and self.day_is_empty(week_ix, day_ix):
            day_ix -= 1
        return day_ix

    def get_previous_day(self, week_ix, day_ix):
        if day_ix:
            day_ix -= 1
        else:
            if week_ix:
                week_ix -= 1
                day_ix = 6
            else:  # we were already on day 0 of week 0
                return (None, None)
        return week_ix, day_ix

    def get_previous_nonempty_day(self, week_ix, day_ix):
        week_ix, day_ix = self.get_previous_day(week_ix, day_ix)
        while week_ix is not None and self.day_is_empty(week_ix, day_ix):
            week_ix, day_ix = self.get_previous_day(week_ix, day_ix)
        return (week_ix, day_ix)

if __name__ == '__main__':
    filename = len(sys.argv) > 1 and sys.argv[1] or 'sheet_001.csv'
    with open(filename, 'r') as infile:
        r_w = ReadWeeks(infile)
        r_w.read_lines()
        print(r_w)
        # r_w.purge_tail()
        # r_w.purge()
        r_w.purge()
        print(r_w)
