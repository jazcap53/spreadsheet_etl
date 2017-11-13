# file: src/extract/read_fns.py
# andrew jarcho
# 2017-01-25

"""
SUMMARY:
=======
read_fns.py contains functions which read the raw input,
extract and format the data of interest, discard incomplete data, and
write the remaining formatted data of interest to stdout.

DETAIL:
======

The Task
---------

The input, a .csv file, is structured in lines as:

    w              Sun   Mon  Tue  Wed  Thu  Fri  Sat
    Sunday Date                    x    x    x    x
                                   x         x    x
                                   x              x
                                                  x


    Sunday Date    x     x    x    x    x    x    x
                   x          x    x         x    x
                              x    x         x
                              x              x
                              x

.
.
.

where each 'x' is a data item we care about (the 'w' at the start of
the file is noise).

A central problem is to extract data from the .csv file so that data
relating to each calendar day are grouped together.

A second problem is that the database cares about 'nights', which may
begin and end with arbitrary data points 'x'.

A third problem is that we must discard data points 'x' that are part
of a 'night' for which we do not have complete data.


Functions
---------

lines_in_weeks_out() structures the data into an intermediate format
consisting of Weeks, Days, and Events. A Week has 7 consecutive (calendar)
Days, beginning with a Sunday. The Events from each Day are grouped
together (note that this is *not* the case in the .csv file).

_manage_output_buffer() converts the Weeks, Days, and Events into strings
and puts the strings into a buffer one Week at a time.

The main unit of interest to the database is a *night*, not a day. We
must discard any night for which we do not have complete data.

_handle_start_of_night() makes sure that only complete nights are written
to output


Week, Day, Event
----------------

Each Event has either 2 or 3 fields; each field is a key/value pair. The
key of the first field of each Event is 'action'. If the value for the
'action' field is 'b' (bedtime), then that Event starts a night.

The first two fields of any key 'action' / value 'b' Event hold data for
the night being started. The third field, with key 'hours', when present,
indicates that the data for the *preceding* night (if there was one) are
complete.

If an 'action: b' event string (i.e., an Event converted to a string) has
NO 'hours' substring, then the data for the preceding night or nights is NOT
complete. In that case, event strings are discarded *in reverse order*
starting with the event string before the current 'action: b' string,
up to and including the most recent 'action: b' event string that *does*
have an 'hours' substring.

The selection of event strings to be discarded is done by the
_handle_start_of_night() member function, as described in the "Functions"
section above.

Event strings not discarded, along with header strings for each calendar
week and day, are written to sys.stdout by default.
"""
import datetime
import re
import logging
import sys

from src.extract.container_objs import validate_segment, Week, Day, Event


read_logger = logging.getLogger('extract.read_fns')


def open_infile(file_read_wrapper):
    """
    :param file_read_wrapper: allows reading from a fake instead of
                              a real file during testing.
    :return: a file handle open for read
    Called by: client code
    """
    return file_read_wrapper.open()


def open_outfile(file_write_wrapper):
    """
    :param file_write_wrapper: allows writing to a fake instead of
                               a real file during testing.
    :return: a file handle open for write
    Called by: client code
    """
    return file_write_wrapper.open()


def lines_in_weeks_out(infile):
    """
    Read lines from .csv file; write Weeks, Days, and Events.

    While there is data to read:
        Read and ignore lines until we see the start of a week
        Call _handle_week() to collect and output a week of data
    If a partial week remains in output buffer:
        Call _handle_leftovers() to output it

    :param infile: a file handle open for read
    :return: None
    Called by: client code
    """
    sunday_date = None
    new_week = None
    are_in_week = False
    are_events = False
    output_buffer = []
    for line in infile:
        line_as_list = line.strip().split(',')[:22]
        is_date_match_found = _re_match_date(line_as_list[0])  # start of week
        if not are_in_week:
            sunday_date, new_week, are_in_week = \
                _look_for_week(is_date_match_found)
        if are_in_week:  # *not* else: _look_for_week() may alter are_in_week
            # _handle_week() outputs good data and discards bad data
            are_events, are_in_week, sunday_date = \
                _handle_week(line_as_list, new_week, output_buffer,
                             sunday_date)
    # handle any data left in buffer
    if sunday_date and are_events and new_week:
        _handle_leftovers(output_buffer, new_week)


# TODO: write docstring
def _look_for_week(date_match_found):
    if not date_match_found:
        return None, None, False  # sunday_date, new_week, in_week
    else:
        sunday_date = _match_to_date_obj(date_match_found)
        # set up a Week
        day_list = [Day(sunday_date +
                        datetime.timedelta(days=x), [])
                    for x in range(7)]
        new_week = Week(*day_list)
        in_week = True
        return sunday_date, new_week, in_week


# TODO: write docstring
def _handle_week(line_as_list, new_week, output_buffer, sunday_date):
    if any(line_as_list):
        # True: have_events
        return _get_events(line_as_list[1:], new_week), True, sunday_date
    else:  # a blank line: our week has ended
        _manage_output_buffer(output_buffer, new_week)
        return False, False, None  # have_events, in_week, sunday_date


def _handle_leftovers(output_buffer, new_week):
    _manage_output_buffer(output_buffer, new_week)


def _re_match_date(field):
    """
    Does field start with a date?

    :param field: a string
    Called by: lines_in_weeks_out()
    """
    m = re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', field)
    return m if m else None


def _match_to_date_obj(m):
    """
    Convert a successful regex match to a datetime.date object
    Called by: lines_in_weeks_out()
    """
    # group(3) is the year, group(1) is the month, group(2) is the day
    dt = [int(m.group(x)) for x in (3, 1, 2)]
    dt_obj = datetime.date(dt[0], dt[1], dt[2])  # year, month, day
    return dt_obj


def _get_events(shorter_line, new_week):
    """
    Add each valid event in shorter_line to new_week.

    :param shorter_line: line_as_list, from lines_in_weeks_out(),
        without its first field
    :param new_week: a Week object
    Called by: lines_in_weeks_out()
    """
    find_events = False
    for ix in range(7):
        # a segment is a list of 3 consecutive fields from the .csv file
        segment = shorter_line[3 * ix: 3 * ix + 3]
        if validate_segment(segment):
            an_event = Event(*segment)
        elif segment == ['', '', '']:
            an_event = None
        else:
            read_logger.warning('segment {} not valid in _get_events()\n'
                                '\tsegment date is {}'.
                                format(segment, new_week[ix].dt_date))
            continue
        if new_week and an_event and an_event.action:
            new_week[ix].events.append(an_event)
            find_events = True
    return find_events


def _manage_output_buffer(buffer, wk):
    """
    Convert the Events in wk into strings and place strings into buffer.

    :param buffer: a list, possibly empty, of header strings and event
                   strings.
    :param wk: a Week object, holding seven Day objects beginning
               with a Sunday. Each Day may have zero or more bedtime
               (action == 'b') Events, as well as zero or more other
               Events.
    :return: None
    Called by: lines_in_weeks_out()
    """
    _append_week_header(buffer, wk)
    for day in wk:
        _append_day_header(buffer, day)
        for event in day.events:
            event_str = 'action: {}, time: {}'.format(event.action,
                                                      event.mil_time)
            if event.hours:
                event_str += ', hours: {:.2f}'.format(float(event.hours))
            if event.action == 'b':
                _handle_start_of_night(buffer, event, day.dt_date)
            buffer.append(event_str)


def _append_week_header(buffer, wk):
    """
    :param buffer: a list, possibly empty, of header strings and event
                   strings.
    :param wk: a Week object, holding seven Day objects beginning
               with a Sunday. Each Day may have zero or more bedtime
               (action == 'b') Events, as well as zero or more other
               Events.
    :return: None
    Called by: _manage_output_buffer()
    """
    wk_header = '\nWeek of Sunday, {}:'.format(wk[0].dt_date)
    wk_header += '\n' + '=' * (len(wk_header) - 2)
    buffer.append(wk_header)


def _append_day_header(buffer, dy):
    """
    :param buffer: a list, possibly empty, of header strings and event
                   strings.
    :param dy: a Day object, which may have zero or more bedtime
               (action == 'b') Events, as well as zero or more other
               Events.
    :return: None
    Called by: _manage_output_buffer()
    """
    dy_header = '    {}'.format(dy.dt_date)  # four leading spaces
    buffer.append(dy_header)


def _handle_start_of_night(buffer, action_b_event, datetime_date,
                           out=sys.stdout):
    """
    Write (only) complete nights from buffer to out.

    A 'b' action Event starts each night of data.
    If any data from the *previous* night are missing, this Event will
        have exactly two key/value elements.
    Otherwise, 'b' action Events have exactly three key/value elements.

    if the Event parameter action_b_event has 3 elements:
        output the entire buffer
        clear() the buffer
    else:
        do not output anything
        pop() lines from the buffer:
            start with the last line that represents an Event
            leave any header lines intact
            stop pop()ping after removing a 3-element 'b' Event

    :param buffer: a list of strings. May contain header lines and/or
                   event lines. Event lines start with 'action: '.
    :param action_b_event: is the first Event for some night.
                           action_b_event will have an 'hours' field <=>
                           we have complete data for the preceding night.
    :param datetime_date: a datetime.date
    :return: None
    Called by: _manage_output_buffer()
    """
    if action_b_event.hours:  # we have complete data for the preceding night
        for line in buffer:  # note: action_b_event is *not* in buffer
            out.write(line + '\n')
        buffer.clear()
    else:
        read_logger.info('Incomplete night(s) before {}'.format(datetime_date))
        for buf_ix in range(len(buffer) - 1, -1, -1):
            this_line = buffer[buf_ix]
            # if we see a 3-element 'b' event, there's good data preceding it
            if _is_complete_b_event_line(this_line):
                buffer.pop(buf_ix)  # pop one last time
                break
            elif _is_event_line(this_line):  # pop only Event lines:
                buffer.pop(buf_ix)          # leave headers in buffer


def _is_complete_b_event_line(line):
    """
    Called by: _handle_start_of_night()
    """
    return re.match(r'action: b, time: \d{1,2}:\d{2}, hours: \d{1,2}\.\d{2}$',
                    line)


def _is_event_line(line):
    """
    Called by: _handle_start_of_night()
    """
    # b events may have 2 or 3 elements
    matchline = r'(?:action: b, time: \d{1,2}:\d{2})' + \
                r'(?:, hours: \d{1,2}\.\d{2})?$'
    # s events may have only 2 elements
    matchline += r'|(?:action: s, time: \d{1,2}:\d{2}$)'
    # w events may have only 3 elements
    matchline += r'|(?:action: w, time: \d{1,2}:\d{2}, ' + \
                 r'hours: \d{1,2}\.\d{2}$)'
    return re.match(matchline, line)
