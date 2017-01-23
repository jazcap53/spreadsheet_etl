# file: lines_to_days.py
# andrew jarcho
# 2017-01-05

# python: 2.7, 3.5


from __future__ import print_function

import datetime
from datetime import date
import re
import sys

from container_objs import validate_segment, Event, Day, Week


class ReadAndPurge:
    """
    Read data from stream into Weeks, Days, and Events.
    """
    try:
        infile = open(sys.argv[1])
    except IndexError:
        print('Usage: {} <input file name>'.format(sys.argv[0]))
        sys.exit(0)

    weeks = []

    def __str__(self):
        ret = ''
        for i in range(len(self.weeks)):
            ret += self.weeks[i].__str__() + '\n'
        return ret


    class Read:

        def __init__(self):
            self.infile = ReadAndPurge.infile
            self.weeks = ReadAndPurge.weeks
            self.sunday_date = None  # the first day of each Week is a Sunday
            self.have_unstored_event = False
            self.new_week = None

        def __str__(self):
            return('Read.__str__() called\n')

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


    class Purge:

        def __init__(self):
            # nonlocal weeks
            self.weeks = ReadAndPurge.weeks

        def __str__(self):
            return('Purge.__str__() called\n')

        def week_is_empty(self, week_ix):
            return all([self.day_is_empty(week_ix, d) for d in range(7)])

        def day_is_empty(self, week_ix, day_ix):
            return not len(self.weeks[week_ix].day_list[day_ix].events)

        def restarts_purge(self, event):
            return event.action == 'b' and (not event.mil_time or not event.hours)

        def stops_purge(self, event):
            if event is None:
                return True
            return event.action == 'b' and event.mil_time and event.hours

        def purge(self):
            purging = True
            event = None
            final_event = self.get_final_event()
            if final_event:  # None or a 4-tuple
                week_ix, day_ix, event_ix, event = final_event
            while event:
                if purging:
                    if self.stops_purge(event):
                        purging = False
                    else:
                        if __debug__:
                            print('popping {}'.format(event))
                        self.weeks[week_ix].day_list[day_ix].events.pop(event_ix)
                else:
                    if self.restarts_purge(event):
                        purging = True
                    else:
                        if __debug__:
                            print('keeping {}'.format(event))
                previous_event = self.get_previous_event(week_ix, day_ix, event_ix)
                if previous_event:  # None or a 4-tuple
                    week_ix, day_ix, event_ix, event = previous_event
                else:
                    event = None

        def get_final_event(self):
            week_ix = self.get_final_nonempty_week()
            if week_ix is not None:
                day_ix = self.get_final_nonempty_day(week_ix)
                event_ix = len(self.weeks[week_ix].day_list[day_ix].events) - 1
                event = self.weeks[week_ix].day_list[day_ix].events[event_ix]
                return (week_ix, day_ix, event_ix, event)
            return None

        def get_previous_event(self, week_ix, day_ix, event_ix):
            """
            pre: week_ix, day_ix, event_ix are not None
            """
            ret_val = None
            if event_ix:
                event_ix -= 1
                event = self.weeks[week_ix].day_list[day_ix].events[event_ix]
            else:
                week_ix, day_ix = self.get_previous_nonempty_day(week_ix, day_ix)
                if week_ix is not None:  # there was a previous nonempty day
                    event_ix = len(self.weeks[week_ix].day_list[day_ix].events) - 1
                    if __debug__:
                        print('week: {}, day: {}, event: {}'.format(week_ix, day_ix, event_ix))
                    event = self.weeks[week_ix].day_list[day_ix].events[event_ix]
            if week_ix is not None:
                ret_val = (week_ix, day_ix, event_ix, event)
            return ret_val

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
