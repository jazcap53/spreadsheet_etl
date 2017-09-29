# file: src/extract/read_fns.py
# andrew jarcho
# 2017-01-25

# python: 3.5


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
controls the data processing: all other functions in this
file are called from read_lines().

read_lines() returns a list of Weeks to the client.
"""


import datetime
import re

from src.extract.container_objs import validate_segment, Week, Day, Event


def open_file(file_read_wrapper):
    """
    file_read_wrapper allows reading from a fake instead of
        a real file during testing.

    Returns: a file handler open for read
    Called by: client code
    """
    return file_read_wrapper.open()


# TODO: fix docstring
def read_lines(infile, weeks):
    """
    Loop:
        Ignore lines until a Sunday is seen.
        Collect data until a blank line is seen.
        Append that data to the output.
    Until:
        EOF.

    Returns: the weeks list
    Called by: client code
    """
    in_week = False
    sunday_date = None
    got_events = False
    new_week = None
    for line in infile:
        line = line.strip().split(',')[:22]
        date_match = _check_for_date(line[0])
        if not in_week and not date_match:
            continue
        elif not in_week and date_match:  # we just found a date_match
            sunday_date = _match_to_date_obj(date_match)
            # collect 7 Days into a day_list
            day_list = [Day(sunday_date +
                            datetime.timedelta(days=x), [])
                        for x in range(7)]
            # create a week
            new_week = Week(*day_list)
            in_week = True
        if in_week:
            if not any(line):
                weeks.append(new_week)
                in_week = False
            else:
                got_events = _get_events(line[1:], new_week)
    if sunday_date and got_events and new_week:
        weeks.append(new_week)
    return weeks


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
    got_events = False
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
                got_events = True
    return got_events
