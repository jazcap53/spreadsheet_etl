# file: src/extract/read_fns.py
# andrew jarcho
# 2017-01-25

# python: 3


"""
The input is structured in lines as:

    Sunday Date   Sun   Mon  Tue  Wed  Thu  Fri  Sat
                                   x    x    x    x
                                   x         x    x
                                   x              x
                                                  x


    Sunday Date    x     x    x    x    x    x    x
                   x          x    x         x    x
                              x    x         x
                              x              x
                              x

    where each 'x' is a data item (event) we care about.

The output is structured into Events, Days, and Weeks.
The Events from each Day are grouped together. A Week
groups 7 consecutive Days, beginning with a Sunday.

Once the input file has been opened, function read_lines()
controls the data processing: all other functions are
called from read_lines().

read_lines() returns a list of Weeks to the client.
"""


import datetime
import re
from collections import namedtuple

from src.extract.container_objs import validate_segment, Week, Day, Event


def open_file(file_read_wrapper):
    """
    Called by: client code
    """
    return file_read_wrapper.open()


def read_lines(infile, weeks, sunday_date=None, do_append_week=False,
               new_week=None):
    """
    Ignore lines that appear before the first Sunday is seen.
    Thereafter, collect data until a blank line is seen.
    Append that data to the output, and resume ignoring lines
    until the next Sunday is seen, or EOF.

    Returns: the weeks list.
    Called by: client code
    """
    WeeksPlus = namedtuple('WeeksPlus', ['weeks', 'sunday_date', 'do_append_week', 'new_week'])
    wks_pls = WeeksPlus(weeks, sunday_date, do_append_week, new_week)
    for line in infile:
        line = line.strip().split(',')
        if not any(line):
            if not wks_pls.sunday_date:     # we're looking for a Sunday
                continue
            else:
                wks_pls = _append_week(wks_pls)
        elif not wks_pls.sunday_date:
            date_match = _check_for_date(line[0])
            if date_match:                  # we've found a Sunday
                wks_pls = wks_pls._replace(sunday_date=_match_to_date_obj(date_match))
                day_list = [Day(wks_pls.sunday_date + datetime.timedelta(days=x), [])
                            for x in range(7)]  # collect 7 Days into a day_list
                wks_pls = wks_pls._replace(new_week=Week(*day_list))  # create a Week
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
    wks_pls.
    Returns: If we have a new Week object, an updated wks_pls
             Else, the function's argument
    Called by: read_lines()
    """
    if all(wks_pls[1: ]):  # if sunday_date and do_append_week and new_week
        my_new_week = wks_pls.new_week
        wks_pls.weeks.append(my_new_week)
        wks_pls = wks_pls._replace(sunday_date=None, do_append_week=False, new_week=None)
    return wks_pls


def _check_for_date(s):
    """
    Is the first element of s a date?
    Called by: read_lines()
    """
    m = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', s)
    return m if m else None


def _match_to_date_obj(m):
    """
    Convert a successful regex match to a datetime.date
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
