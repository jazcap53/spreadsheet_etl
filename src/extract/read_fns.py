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
    weeks_plus = [weeks, sunday_date, do_append_week, new_week]
    for line in infile:
        line = line.strip().split(',')
        # if we got a blank line, check whether we have a sunday (i.e., we're in a week)
            # if no sunday: continue
            # if yes sunday: append the new week to our output, and set sunday_date to None
        if not any(line):      # we had a blank row in the spreadsheet
            if not weeks_plus[1]:  # sunday_date
                continue
            else:
                weeks_plus = _append_week(weeks_plus)
        # if we got a non-blank line but haven't seen a sunday yet
            # check that the line starts with a sunday
            # if it does:
                # retrieve the sunday date
                # create a new week for that date
            # if it doesn't:
                # continue
        elif not weeks_plus[1]:  # we haven't seen a Sunday yet this week
            date_match = _check_for_date(line[0])
            if date_match:
                weeks_plus[1] = _match_to_date_obj(date_match)
                day_list = [Day(weeks_plus[1] + datetime.timedelta(days=x), [])
                        for x in range(7)]
                weeks_plus[3] = Week(*day_list)
                #### weeks_plus[0].append(weeks_plus[3])  # ???
            else:
                continue
        # skip header line  TODO: REMOVE -- SUPERFLUOUS
        elif _is_header(line):
            continue
        if any(line[1: ]):
            weeks_plus[2: ] = _get_events(line[1: ], weeks_plus[3])
            # do_append_week, new_week = _get_events(line[1:], new_week)
            # weeks_plus = [weeks, sunday_date, do_append_week, new_week]
    # save any remaining unstored data
    weeks_plus = _append_week(weeks_plus)
    return weeks_plus[0]


def _is_header(l):
    """
    Called by: read_lines()
    """
    return l[1] == 'Sun'


def _append_week(weeks_plus):
    """
    If we have a new Week object, append it to the weeks element of
    weeks_plus.
    Returns: If we have a new Week object, an updated weeks_plus
             Else, the function's argument
    Called by: read_lines()
    """
    if all(weeks_plus[1: ]):  # if sunday_date and do_append_week and new_week
        weeks_plus[0].append(weeks_plus[3])
        weeks_plus[1: ] = [None, False, None]
        # return [weeks, None, False, None]
    return weeks_plus


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
