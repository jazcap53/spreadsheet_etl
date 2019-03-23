# file: src/extract/read_fns.py
# andrew jarcho
# 2017-01-25

"""
SUMMARY:
=======
Class Extract in read_fns.py reads the raw input, extracts and formats
the data of interest, discards incomplete data, and writes the remaining data
of interest to stdout.

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
begin and end with arbitrary data points 'x'. Each night is associated
with a calendar day in the db.

A third problem is that we must discard data points 'x' that are part
of a 'night' for which we do not have complete data.


Principal methods
-----------------

lines_in_weeks_out() structures the data into an intermediate format
consisting of Weeks, Days, and Events. A Week has 7 consecutive (calendar)
Days, beginning with a Sunday. The Events from each Day are grouped
together.

_manage_output_buffer() converts the Weeks, Days, and Events into strings,
and puts the strings into the output buffer one Week at a time.

_handle_start_of_night() makes sure that only complete nights are written
to output


Week, Day, Event
----------------

Each Event has either 2 or 3 fields; each field is a key/value pair. The
key of the first field of each Event is 'action'. If the value for an
'action' field is 'b', then that Event starts a night.

The first two fields of any <'action': 'b'> Event hold data for
the night being started. If a third field is present, this
indicates that the data for the *preceding* night (if there was one)
are complete.

If an <'action: b'> event has NO third field, then the data for the
preceding night or nights are NOT complete. In that case, events are
discarded *in reverse order* starting with the event before the current
<'action: b'> event, up to and including the most recent <'action: b'>
event string that *does* have a third field.

Event strings not discarded, along with header strings for each calendar
week and day, are written to sys.stdout by default.
"""
import datetime
import re
import logging
import sys

from container_objs import validate_segment, Week, Day, Event


read_logger = logging.getLogger('extract.read_fns')
read_logger.setLevel('DEBUG')


def open_infile(filename):
    """
    :param filename: name of file to be read
    :return: a file handle open for read
    Called by: client code
    """
    return filename.open()


class Extract:
    NULL_DATE = datetime.date(datetime.MINYEAR, 1, 1)

    def __init__(self, infile):
        """
        :param infile: A file handle open for read
        """
        self.infile = infile
        self.sunday_date = Extract.NULL_DATE
        self.new_week = None
        self.we_are_in_week = False
        self.have_events = False
        self.output_buffer = []
        self.line_as_list = []

    def lines_in_weeks_out(self):
        """
        Read lines from .csv file; output weeks, days, and events

        :return: None
        Called by: client code
        """
        for line in self.infile:
            self.line_as_list = line.strip().split(',')[:22]
            date_match = self._re_match_date(self.line_as_list[0])
            if not self.we_are_in_week:
                self._look_for_week(date_match)
            if self.we_are_in_week:  # 'if' is correct here
                # output good data and discard bad data
                self._handle_week()
        # handle any data left in buffer
        self._handle_leftovers()

    @staticmethod
    def _re_match_date(field):
        """
        Does param 'field' start with a date?

        :param field: a string
        :return: a match object for a date in format dd/mm/yyyy
        Called by: lines_in_weeks_out()
        """
        return re.match(r'(\d{1,2})/(\d{1,2})/(\d{4})', field)

    def _look_for_week(self, date_match):
        """
        Determine whether current input line represents the start of a week.

        :param date_match: a match object for a date in format dd/mm/yyyy
        :return: None
        Called by: lines_in_weeks_out()
        """
        self.sunday_date = Extract.NULL_DATE
        self.new_week = None
        if date_match:
            self.sunday_date = self._match_to_date_obj(date_match)
            if self._is_a_sunday(self.sunday_date):
                # set up a Week
                day_list = [Day(self.sunday_date +
                                datetime.timedelta(days=x), [])
                            for x in range(7)]
                self.new_week = Week(*day_list)
                self.we_are_in_week = True
            else:
                read_logger.warning('Non-Sunday date {} found in input'.
                                    format(self.sunday_date))
                self.sunday_date = Extract.NULL_DATE

    @staticmethod
    def _is_a_sunday(dt_date):
        """
        Tell whether the parameter represents a Sunday

        :param dt_date: a datetime.date object
        :return: bool: is dt_date a Sunday
        Called by: _look_for_week()
        """
        if dt_date == Extract.NULL_DATE:
            return False
        return dt_date.weekday() == 6

    def _handle_week(self):
        """
        if there are valid events in self.line_as_list:
            call self._get_events() to store them as Event objects in Week
            object new_week
        else:
            call self._manage_output_buffer() to write good data, discard
            incomplete data from self.output_buffer

        :return: None
        Called by: lines_in_weeks_out()
        """
        self.have_events = False
        self.we_are_in_week = False
        if any(self.line_as_list):
            self._get_events()
            if self.have_events:
                self.we_are_in_week = True
        else:  # we saw a blank line: our week has ended
            self._manage_output_buffer()

    def _handle_leftovers(self):
        """
        If there is data left in self.output_buffer, calls
                self._manage_output_buffer().

        :return: None
        Called by: lines_in_weeks_out()
        """
        if self.sunday_date and self.have_events and self.new_week:
            self._manage_output_buffer()

    @staticmethod
    def _match_to_date_obj(m):
        """
        Convert a successful regex match to a datetime.date object

        :return: a datetime.date object
        Called by: lines_in_weeks_out()
        """
        if m:
            # group(3) is the year, group(1) is the month, group(2) is the day
            dt = [int(m.group(x)) for x in (3, 1, 2)]
            return datetime.date(dt[0], dt[1], dt[2])  # year, month, day
        else:
            return Extract.NULL_DATE

    def _get_events(self):
        """
        Add each valid event in self.line_as_list to self.new_week.

        :return: None
        Called by: lines_in_weeks_out()
        """
        shorter_line = self.line_as_list[1:]
        self.have_events = False
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
                                    format(segment,
                                           self.new_week[ix].dt_date))
                continue
            if self.new_week and an_event and an_event.action:
                self.new_week[ix].events.append(an_event)
                self.have_events = True

    def _manage_output_buffer(self):
        """
        Convert the Events in self.new_week into strings and place the strings
        in output buffer.

        :return: None
        Called by: lines_in_weeks_out()
        """
        self._append_week_header()
        for day in self.new_week:
            self._append_day_header(day)
            for event in day.events:
                event_str = 'action: {}, time: {}'.format(event.action,
                                                          event.mil_time)
                if event.hours:
                    event_str += ', hours: {:.2f}'.format(float(event.hours))
                if event.action == 'b':
                    self._handle_start_of_night(event, day.dt_date)
                self.output_buffer.append(event_str)

    def _append_week_header(self):
        """
        :return: None
        Called by: _manage_output_buffer()
        """
        wk_header = '\nWeek of Sunday, {}:'.format(self.new_week[0].dt_date)
        wk_header += '\n' + '=' * (len(wk_header) - 2)
        self.output_buffer.append(wk_header)

    def _append_day_header(self, day):
        """
        :return: None
        Called by: _manage_output_buffer()
        """
        dy_header = '    {}'.format(day.dt_date)  # four leading spaces
        self.output_buffer.append(dy_header)

    def _handle_start_of_night(self, action_b_event, datetime_date,
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

        :param action_b_event: is the first Event for some night.
                               action_b_event will have an 'hours' field iff
                               we have complete data for the preceding night.
        :param datetime_date: a datetime.date
        :param out: output destination
        :return: None
        Called by: _manage_output_buffer()
        """
        if action_b_event.hours:  # we have complete data for preceding night
            for line in self.output_buffer:  # action_b_event is NOT in buffer
                print(line, file=out)
            self.output_buffer.clear()
        else:
            read_logger.info('Incomplete night(s) before {}'.
                             format(datetime_date))
            # pop incomplete data from output buffer
            for buf_ix in range(len(self.output_buffer) - 1, -1, -1):
                this_line = self.output_buffer[buf_ix]
                # if we see a 3-element 'b' event, there's good data before it
                if self._match_complete_b_event_line(this_line):
                    # pop one last time; change 'b' event to 'N' event
                    no_data_line = self.output_buffer.pop(buf_ix).replace('b', 'N', 1)
                    print(no_data_line, file=out)
                    break
                elif self._match_event_line(this_line):  # pop only Event lines
                    self.output_buffer.pop(buf_ix)  # leave headers in buffer

    @staticmethod
    def _match_complete_b_event_line(line):
        """
        Called by: _handle_start_of_night()
        """
        return re.match(r'action: b, time: \d{1,2}:\d{2},'
                        ' hours: \d{1,2}\.\d{2}$',
                        line)

    @staticmethod
    def _match_event_line(line):
        """
        Called by: _handle_start_of_night()
        """
        # b events may have 2 or 3 elements
        match_line = r'(?:action: b, time: \d{1,2}:\d{2})' + \
                     r'(?:, hours: \d{1,2}\.\d{2})?$'
        # s events may only have 2 elements
        match_line += r'|(?:action: s, time: \d{1,2}:\d{2}$)'
        # w events may only have 3 elements
        match_line += r'|(?:action: w, time: \d{1,2}:\d{2}, ' + \
                      r'hours: \d{1,2}\.\d{2}$)'
        return re.match(match_line, line)
