# file: src/read_fns.py
# andrew jarcho
# 2017-01-25

# python: 2.7, 3.5, 3.6


from __future__ import print_function

import re
import datetime

from container_objs import validate_segment, Week, Day, Event, weeks


def open_file(file_read_wrapper):
    """
    Called by: client code
    """
    return file_read_wrapper.open()


# TODO: make this function easier to read
def read_lines(infile, weeks, sunday_date=None, have_unstored_event=False,
        new_week=None):
    """
    Called by: client code
    """
    for line in infile:
        line = line.strip().split(',')
        if is_header(line):
            continue
        if not any(line):  # if we had a blank row in the spreadsheet
            # store previous week, if any
            weeks, sunday_date, have_unstored_event, new_week = store_week(
                    weeks, sunday_date, have_unstored_event, new_week)
            continue
        if not sunday_date:
            found_match = check_for_date(line[0])
            if not found_match:  # we are not at the start of a week
                continue
            sunday_date = match_to_date_obj(found_match)
            day_list = []
            for x in range(7):
                day_list.append(Day(sunday_date + datetime.timedelta(days=x), []))
            new_week = Week(*day_list)
        if any(line[1:]):
            have_unstored_event, new_week = load_line(line[1:], new_week)
    # save any left-over unstored data
    store_week(weeks, sunday_date, have_unstored_event, new_week)
    return weeks


def is_header(l):
    """
    Called by: read_lines()
    """
    return l[1] == 'Sun'


def store_week(weeks, sunday_date, have_unstored_event, new_week):
    """
    Called by: read_lines()
    """
    if sunday_date and have_unstored_event and new_week:
        weeks.append(new_week)
        return weeks, None, False, None
    return weeks, sunday_date, have_unstored_event, new_week


def check_for_date(s):
    """
    Called by: read_lines()
    """
    # TODO: replace with more sophisticated test?
    m = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', s)
    return m if m else None


def match_to_date_obj(m):
    """
    Called by: read_lines()
    """
    # group(3) is the year, group(1) is the month, group(2) is the day
    d = [int(m.group(x)) for x in (3, 1, 2)]
    d_obj = datetime.date(d[0], d[1], d[2])  # year, month, day
    return d_obj


def load_line(line, new_week):
    """
    Called by: read_lines()
    """
    have_unstored_event = False
    for ix in range(7):
        segment = line[3*ix: 3*ix + 3]
        if validate_segment(segment):
            an_event = Event(*segment)
            if new_week and an_event.action:
                new_week[ix].events.append(an_event)
                have_unstored_event = True
    return have_unstored_event, new_week
