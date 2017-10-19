# file: src/extract/read_fns.py
# andrew jarcho
# 2017-01-25

# python: 3.5

# TODO: fix below docstring
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
def read_lines(infile):
    """
    Loop:
        Ignore lines until a Sunday is seen.
        Collect data until a blank line is seen.
        Append that data to the output.
    Until:
        EOF.

    Called by: client code
    """
    in_week = False
    sunday_date = None
    got_events = False
    new_week = None
    lines_buffer = []
    for line in infile:
        line = line.strip().split(',')[:22]
        date_match = _check_for_date(line[0])
        if not in_week and not date_match:
            continue
        elif not in_week and date_match:  # we just found a date_match
            sunday_date = _match_to_date_obj(date_match)
            # create a day_list of 7 (empty) Days
            day_list = [Day(sunday_date +
                            datetime.timedelta(days=x), [])
                        for x in range(7)]
            new_week = Week(*day_list)
            in_week = True
        if in_week:
            if not any(line):
                _buffer_week(new_week, lines_buffer)
                in_week = False
                sunday_date = None
            else:
                got_events = _get_events(line[1:], new_week)
    # save any remaining unstored data
    if sunday_date and got_events and new_week:
        _buffer_week(new_week, lines_buffer)


def _check_for_date(segment):
    """
    Does segment start with a date?
    Called by: read_lines()
    """
    m = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', segment)
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
        # a segment is a list of 3 consecutive fields from the .csv file
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


# TODO: write docstring, comments
def _buffer_week(wk, buffer):
    wk_header = '\nWeek of Sunday, {}:\n'.format(wk[0].dt_date)
    underscores = '=' * (len(wk_header) - 2)
    buffer.append(wk_header + underscores)
    for day in wk:
        dy_header = '    ' + '{}'.format(day.dt_date)
        buffer.append(dy_header)
        for event in day.events:
            event_str = 'action: {}, time: {}'.format(event.action,
                                                      event.mil_time)
            if event.hours:
                event_str += ', hours: {:.2f}'.format(float(event.hours))
            if event.action == 'b':
                _print_complete_days(buffer, event)
            buffer.append(event_str)


# TODO: complete docstring
def _print_complete_days(buffer, event):
    """
    Write complete days (only) from buffer to stdout
    Called by: _buffer_week()
    """
    if event.hours:  # we have a complete Day
        for line in buffer:
            print(line)
        buffer.clear()
    else:  # day is *incomplete*
        for buf_ix in range(len(buffer) - 1, -1, -1):  # pop lines
            this_line = buffer[buf_ix]
            # if we find a 3-element 'b' event
            if this_line != '\n' and this_line[8] == 'b' and \
                            len(this_line) > 21:
                buffer.pop(buf_ix)
                break  # quit popping
            if this_line[:6] == 'action':  # pop only 'action' lines
                buffer.pop(buf_ix)
