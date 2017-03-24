# file: src/extract/read_fns.py
# andrew jarcho
# 2017-01-25

# python: 2.7, 3.5


from __future__ import print_function

import sys
import re
import datetime
from collections import namedtuple

from src.extract.container_objs import validate_segment, Week, Day, Event, weeks


def open_file(file_read_wrapper):
    """
    Called by: client code
    """
    return file_read_wrapper.open()


# TODO: make this function easier to read
# TODO: get rid of do_append_week? sunday_date? new_week?
def read_lines(infile, weeks, sunday_date=None, do_append_week=False,
               new_week=None):
    """
    Read and discard lines until a Sunday marker is found.
    Then create a Week as a list of 7 Days, and insert data into it
    until a blank line is read. On reading a blank line, append the
    Week just read to the weeks list.
    Returns: the weeks list.
    Called by: client code
    """
    WeeksPlus = namedtuple('WeeksPlus', ['weeks', 'sunday_date', 'do_append_week', 'new_week'])
    wks_pls = WeeksPlus(weeks, sunday_date, do_append_week, new_week)
    for line in infile:
        line = line.strip().split(',')
        if not any(line):      # we had a blank row in the spreadsheet
            if not wks_pls.sunday_date:
                continue
            else:
                wks_pls = _append_week(wks_pls)
        elif not wks_pls.sunday_date:  # we haven't seen a Sunday yet this week
            date_match = _check_for_date(line[0])
            if date_match:
                wks_pls = wks_pls._replace(sunday_date=_match_to_date_obj(date_match))
                day_list = [Day(wks_pls.sunday_date + datetime.timedelta(days=x), [])
                        for x in range(7)]
                wks_pls = wks_pls._replace(new_week=Week(*day_list))
            else:
                continue
        if any(line[1: ]):
            got_events = _get_events(line[1: ], wks_pls.new_week)
            wks_pls = wks_pls._replace(do_append_week=got_events[0], new_week=got_events[1])
    # save any remaining unstored data
    wks_pls = _append_week(wks_pls)
    return wks_pls.weeks


def _append_week(wks_pls):
    """
    If we have a new Week object, append it to the weeks element of
    weeks_plus.
    Returns: If we have a new Week object, an updated weeks_plus
             Else, the function's argument
    Called by: read_lines()
    """
    if all(wks_pls[1: ]):  # if sunday_date and do_append_week and new_week
        my_new_week = wks_pls.new_week
        wks_pls.weeks.append(my_new_week)
        wks_pls = wks_pls._replace(sunday_date=None, do_append_week=False, new_week=None)
        # return [weeks, None, False, None]
    return wks_pls


def _check_for_date(s):
    """
    Called by: read_lines()
    """
    # TODO: replace with more sophisticated test?
    m = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', s)
    return m if m else None


def _match_to_date_obj(m):
    """
    Called by: read_lines()
    """
    # group(3) is the year, group(1) is the month, group(2) is the day
    d = [int(m.group(x)) for x in (3, 1, 2)]
    d_obj = datetime.date(d[0], d[1], d[2])  # year, month, day
    return d_obj


def _get_events(line, new_week):
    """
    Add each valid event in line to new_week.
    Called by: read_lines()
    """
    do_append_week = False
    for ix in range(7):
        # a segment is a list of 3 consecutive items from the .csv file
        segment = line[3*ix: 3*ix + 3]
        if validate_segment(segment):
            try:
                an_event = Event(*segment)
            except ValueError:
                continue
            if new_week and an_event.action:
                new_week[ix].events.append(an_event)
                do_append_week = True
    return do_append_week, new_week
