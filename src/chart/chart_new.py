#!/usr/bin/env python3


# file: chart_new.py
# andrew jarcho
# 10/2018
"""
Create a Timeline Chart from the input data.
"""
import argparse
from datetime import datetime, timedelta
from collections import namedtuple
import logging
import logging.handlers
import re


BLACK_INK = u'\u2588'
WHITE_PAPER = u'\u0020'
GRAY = u'\u2591'


class Chart:
    """
    Create a sleep chart from input data.

    Sample input (from file named as c.l.a.):

        2016-12-10
action: b, time: 0:00, hours: 9.00
action: w, time: 5:15, hours: 5.25
action: s, time: 10:30
action: w, time: 11:30, hours: 1.00
action: s, time: 16:00
action: w, time: 17:00, hours: 1.00
action: b, time: 22:30, hours: 7.25

Week of Sunday, 2016-12-11:
==========================
    2016-12-11
action: w, time: 0:15, hours: 1.75
action: s, time: 2:30
action: w, time: 5:15, hours: 2.75
action: s, time: 11:00
action: w, time: 12:00, hours: 1.00
action: s, time: 17:15
action: w, time: 18:00, hours: 0.75
action: s, time: 19:15
action: w, time: 20:15, hours: 1.00

    Corresponding output (to stdout):

2016-12-10 |█████████████████████                     ████                  ████                      ██████|
            12a 1   2   3   4   5   6   7   8   9   10  11  12p 1   2   3   4   5   6   7   8   9   10  11
2016-12-11 |█         ███████████                       ████                     ███     ████               |
    """
    def __init__(self, args):
        self.DEBUG = args.debug
        self.QS_IN_DAY = 96  # 24 * 4 quarter hours in a day
        self.ASLEEP = 'x' if self.DEBUG else BLACK_INK
        self.AWAKE = 'o' if self.DEBUG else WHITE_PAPER
        self.NO_DATA = '-' if self.DEBUG else GRAY
        self.Triple = namedtuple('Triple', ['start', 'length', 'symbol'],
                                 defaults=[0, 0, self.NO_DATA])
        self.QuartersCarried = namedtuple('QuartersCarried',
                                          ['length', 'symbol'],
                                          defaults=[0, self.NO_DATA])
        self.curr_line = ''
        self.curr_sunday = ''
        self.infilename = args.infilename
        self.outfilename = args.outfilename
        self.infile = None
        self.outfile = open(self.outfilename, 'w') if self.outfilename else None
        self.last_date_read = None
        self.last_sleep_state = self.NO_DATA
        self.last_sleep_time = None
        self.last_start_posn = None
        self.output_date = '2016-12-04'
        self.output_row = [self.NO_DATA] * self.QS_IN_DAY
        self.quarters_carried = self.QuartersCarried(0, self.NO_DATA)
        self.re_decimal_hour = None
        self.re_hr_min_time = None
        self.re_iso_date = None
        self.sleep_state = self.NO_DATA
        self.spaces_left = self.QS_IN_DAY

    def read_file(self):
        """
        Send each line of file to parser.

        :yield: a parsed input line (a Triple namedtuple)
        :return: None
        Called by: main()
        """
        with open(self.infilename) as self.infile:
            while self._get_a_line():
                parsed_input_line = self._parse_input_line()
                if parsed_input_line.start == -1:
                    continue
                yield parsed_input_line

    def _get_a_line(self):
        """
        Get next input line, discarding blank lines and '======'s

        :return: True if a line was retrieved
                 False otherwise (i.e., at eof or on bad input)
        Called by: read_file()
        """
        self.curr_line = self.infile.readline().strip()
        if self.curr_line == '':  # discard exactly one blank line
            self.curr_line = self.infile.readline().strip()
        if self.curr_line.startswith('Week of Sunday, '):
            self.curr_sunday = self.curr_line[16: -1]
            self.infile.readline()  # discard '============' line
            self.curr_line = self.infile.readline().strip()
        return self.curr_line != ''

    def _parse_input_line(self):
        """
        :return: a 'Triple' namedtuple holding
                     a start position, (start)
                     a count of quarter hours, (length)
                     a unicode character (ASLEEP, AWAKE, or NO_DATA) (symbol)
        Called by: read_file()
        """
        if not self.curr_line:
            raise ValueError('self.curr_line is empty in _parse_input_line()')
        if re.match(r'\d{4}-\d{2}-\d{2}$', self.curr_line):
            return self._handle_date_line(self.curr_line)
        return self._handle_action_line(self.curr_line)

    def _handle_date_line(self, line):
        """

        :pre: line is non-empty

        :param line:
        :return:
        Called by _parse_input_line()
        """
        if self.last_date_read is None:
            self.last_start_posn = 0
            self.last_date_read = line
            return self.Triple(-1, -1, -1)  # get more input
        if self.sleep_state == self.NO_DATA:
            quarters_to_output = self.QS_IN_DAY - self.last_start_posn
            return self.Triple(self.last_start_posn, quarters_to_output,
                               self.sleep_state)
        self.last_date_read = line
        return self.Triple(-1, -1, -1)  # get more input

    def _handle_action_line(self, line):
        """
        If a complete Triple is not yet available, return a
        Triple with values (-1, -1, -1).
        Otherwise, return the complete Triple.

        :pre: line starts with 'action: '

        :param line:
        :return: a Triple (a namedtuple) holding
                     a start position,
                     a count of quarter hours,
                     a unicode character (ASLEEP, AWAKE, NO_DATA)
        Called by: _parse_input_line()
        """
        if line[8] in 'bsY':
            self.last_sleep_time = self._get_time_part(line)
            self.last_start_posn = self._get_start_posn(line)
            self.sleep_state = self.ASLEEP
            return self.Triple(-1, -1, -1)  # get more input
        if line[8] == 'w':
            wake_time = self._get_time_part(line)
            duration = self._get_duration(wake_time, self.last_sleep_time)
            length = self._get_num_chunks(duration)
            self.sleep_state = self.AWAKE
            return self.Triple(self.last_start_posn, length, self.ASLEEP)
        if line[8] == 'N':
            self.last_sleep_time = self._get_time_part(line)
            self.last_start_posn = self._get_start_posn(line)
            self.sleep_state = self.NO_DATA
            return self.Triple(-1, -1, -1)  # get more input
        # raise ValueError(f"Bad 'action: ' value in line {line}")   DON'T DO THIS!
        return None

    @staticmethod
    def _get_time_part(cur_l):
        """
        Extract and return the time part of its string argument.

        Input time may be in 'h:mm' or 'hh:mm' format.
        Called by: _process_curr().
        Returns: Extracted time as a string in 'hh:mm' format.
        """
        end_pos = cur_l.rfind(', hours: ')
        out_time = cur_l[17:] if end_pos == -1 else cur_l[17: end_pos]
        if len(out_time) == 4:
            out_time = '0' + out_time
        return out_time

    def _get_duration(self, w_time, s_time):
        """
        Calculate the interval between w_time and s_time.

        Arguments are strings representing times in 'hh:mm' format.
        get_duration() calculates the interval between them as a
        string in decimal format e.g.,
            04.25 for 4 1/4 hours
        Called by: _process_curr()
        Returns: the calculated interval, whose value will be
                non-negative.
        """
        w_time_list = list(map(int, w_time.split(':')))
        s_time_list = list(map(int, s_time.split(':')))
        if w_time_list[1] < s_time_list[1]:  # wake minute < sleep minute
            w_time_list[1] += 60
            w_time_list[0] -= 1
        if w_time_list[0] < s_time_list[0]:  # wake hour < sleep hour
            w_time_list[0] += 24
        dur_list = [(w_time_list[x] - s_time_list[x])
                    for x in range(len(w_time_list))]
        duration = str(dur_list[0])
        if len(duration) == 1:  # change hour from '1' to '01', e.g.
            duration = '0' + duration
        duration += self._quarter_hour_to_decimal(dur_list[1])
        return duration

    def _quarter_hour_to_decimal(self, quarter):
        """
        Convert an integer number of minutes into a decimal string

        Argument is a number of minutes past the hour. If that number
        is a quarter-hour, convert it to a decimal quarter represented
        as a string.

        Called by: _get_duration()
        Returns: a number of minutes represented as a decimal fraction
        """
        valid_quarters = (0, 15, 30, 45)
        if quarter not in valid_quarters:
            quarter = self._get_closest_quarter(quarter)
        return Chart._quarter_to_decimal(quarter)

    @staticmethod
    def _quarter_to_decimal(quarter):
        """
        0 => '.00', 15 => '.25', 30 => '.50', 45 => '.75'

        "pre: quarter % 15 == 0"
        Called by: _quarter_hour_to_decimal()
        """
        return '.' + str(quarter // 3 * 5).zfill(2)

    @staticmethod
    def _get_closest_quarter(q: int):
        """
        Coerce a number of minutes q to the nearest quarter hour.

        :return: an integer in {0, 15, 30, 45}
        """
        if q < 8:
            closest_quarter = 0
        elif 8 <= q < 23:
            closest_quarter = 15
        elif 23 <= q < 37:
            closest_quarter = 30
        elif q < 60:
            closest_quarter = 45
        else:
            raise ValueError(f'q must be < 60 in {__name__}')
        return closest_quarter

    def make_output(self, read_file_iterator):
        """
        Fill a new day (output) row. Start the row with any
        left over quarters.

        :param: read_file_iterator yields parsed input lines (Triples)
        :return: None
        Called by: main()
        """
        row_out = self.output_row[:]
        self.spaces_left = self.QS_IN_DAY

        while True:
            try:
                curr_triple = next(read_file_iterator)
            except StopIteration:
                if row_out != self.output_row:
                    self._write_output(row_out)
                return

            row_out = self._insert_leading_sleep_states(curr_triple, row_out)
            # the next line may update self.quarters_carried.length
            row_out = self._insert_to_row_out(curr_triple, row_out)
            if not self.spaces_left:
                self._write_output(row_out)  # advances self.output_date
                row_out = self.output_row[:]  # get fresh copy of row to output
                self.spaces_left = self.QS_IN_DAY
            if self.quarters_carried.length:
                row_out = self._handle_quarters_carried(row_out)

    def _insert_leading_sleep_states(self, curr_triple, row_out):
        """
        Write sleep states onto row_out from current position to start
        of curr_triple.
        :param curr_triple:
        :param row_out:
        :return:
        Called by: make_output()
        """
        curr_posn = self.QS_IN_DAY - self.spaces_left
        if curr_posn < curr_triple.start:
            row_out = self._fill_gap(curr_posn, curr_triple, row_out)
        elif curr_posn == curr_triple.start:
            pass  # no gap
        else:
            row_out = self._finish_row(curr_posn, row_out)
            if curr_triple.start > 0:
                triple_to_insert = self.Triple(0, curr_triple.start,
                                               self.sleep_state)
                row_out = self._insert_to_row_out(triple_to_insert, row_out)
        self.last_sleep_state = self.sleep_state
        return row_out

    def _finish_row(self, curr_posn, row_out):
        triple_to_insert = self.Triple(curr_posn,
                                       self.QS_IN_DAY - curr_posn,
                                       self.last_sleep_state)
        row_out = self._insert_to_row_out(triple_to_insert, row_out)
        if self._is_complete(triple_to_insert, row_out):
            self._write_output(row_out)
        row_out = self._reset_row()
        return row_out

    def _fill_gap(self, curr_posn, curr_triple, row_out):
        triple_to_insert = self.Triple(curr_posn,
                                       curr_triple.start - curr_posn,
                                       self.last_sleep_state)
        return self._insert_to_row_out(triple_to_insert, row_out)

    def _is_complete(self, triple_to_insert, row_out):
        if not row_out.count(self.NO_DATA) or \
                triple_to_insert.start + triple_to_insert.length == \
                self.QS_IN_DAY:
            return True
        return False

    def _reset_row(self):
        self.spaces_left = self.QS_IN_DAY
        return self.output_row[:]

    def _handle_quarters_carried(self, curr_output_row):
        curr_output_row = self._insert_to_row_out(
            self.Triple(0, self.quarters_carried.length,
                        self.quarters_carried.symbol), curr_output_row)
        self.quarters_carried = self.quarters_carried._replace(length=0)
        return curr_output_row

    def _insert_to_row_out(self, triple, output_row):
        finish = triple.start + triple.length
        if finish > self.QS_IN_DAY:
            self.quarters_carried = self.QuartersCarried(finish - self.QS_IN_DAY, triple.symbol)
            triple = triple._replace(length=triple.length - self.quarters_carried.length)
        for i in range(triple.start, triple.start + triple.length):
            if self.DEBUG is True:
                if not i % 4:
                    output_row[i] = triple.symbol.upper()
                else:
                    output_row[i] = triple.symbol.lower()
            else:
                output_row[i] = triple.symbol
            self.spaces_left -= 1
        return output_row

    def get_curr_posn(self):
        return self.QS_IN_DAY - self.spaces_left

    def _write_output(self, my_output_row):
        """

        :param my_output_row:
        :return:
        Called by: make_output()
        """
        extended_output_row = []
        for _, val in enumerate(my_output_row):
            extended_output_row.append(val)
        print(f'{self.output_date} |{"".join(extended_output_row)}|',
              file=self.outfile)
        self.output_date = self.advance_output_date(self.output_date)

    def advance_date(self, my_date, make_ruler=False):
        """

        :param my_date:
        :param make_ruler:
        :return:
        Called by: advance_input_date(), advance_output_date()
        """
        date_as_datetime = datetime.strptime(my_date, '%Y-%m-%d')
        if make_ruler and date_as_datetime.date().weekday() == 5:
            print(self.create_ruler(), file=self.outfile)
        date_as_datetime += timedelta(days=1)
        return date_as_datetime.strftime('%Y-%m-%d')

    def advance_input_date(self, my_input_date):
        return self.advance_date(my_input_date)

    def advance_output_date(self, my_output_date):
        return self.advance_date(my_output_date, True)

    def _get_num_chunks(self, my_str):
        """
        Obtain from an interval the number of 15-minute chunks it contains
        :return: int: the number of chunks
        Called by: read_file()
        """
        if my_str:
            m = re.search(self.re_decimal_hour, my_str)
            assert bool(m)
            return (int(m.group(1)) * 4 +  # 4 chunks per hour
                    int(m.group(2)) // 25) % self.QS_IN_DAY  # m.group(2) is decimal
        return 0

    def _get_start_posn(self, time_str):
        """
        Obtain, from a time string, its starting position in a line of output.

        Called by: read_file()
        :param time_str: a time expressed as 'HH:MM'
        :return: int: the starting position
        """
        if time_str:
            m = re.search(self.re_hr_min_time, time_str)
            assert bool(m)
            return (int(m.group(1)) * 4 +  # 4 output chars per hour
                    int(m.group(2)) // 15) % self.QS_IN_DAY
        return 0

    def compile_iso_date(self):
        """
        :return: None
        Called by: main()
        """
        self.re_iso_date = re.compile(r' \d{4}-\d{2}-\d{2} \|')

    def compile_decimal_hour(self):
        """
        :return: None
        Called by: main()
        """
        self.re_decimal_hour = re.compile(r'(\d{1,2})\.(\d{2})')

    def compile_hr_min_time(self):
        """
        :return:
        Called by: main()
        """
        self.re_hr_min_time = re.compile(r'(\d{1,2}):(\d{2})')

    @staticmethod
    def create_ruler():
        ruler = list(str(x) for x in range(12)) * 2
        for i, _ in enumerate(ruler):
            if i == 0:
                ruler[i] = '12a'
            elif i == 12:
                ruler[i] = '12p'
        ruler_line = ' ' * 12 + ''.join(v.ljust(4, ' ') for v in ruler)
        return ruler_line


def set_up_loggers():
    # from: https://docs.python.org/3/howto/
    # logging-cookbook.html#network-logging
    root_logger = logging.getLogger('')
    root_logger.setLevel(logging.INFO)
    socket_handler = logging.handlers.SocketHandler('localhost',
                                                    logging.handlers.
                                                    DEFAULT_TCP_LOGGING_PORT)
    # don't bother with a formatter, since a socket handler sends the event as
    # an unformatted pickle
    root_logger.addHandler(socket_handler)
    # end cookbook code

    # read_logger will need a formatter since it is writing to file
    chart_logger = logging.getLogger('extract.read_fns')
    chart_logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler('src/extract/read_fns.log', mode='w')
    formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    chart_logger.addHandler(file_handler)
    chart_logger.propagate = False


def main():
    set_up_loggers()
    logging.info('chart start')
    args = get_parse_args()
    chart = Chart(args)
    chart.compile_decimal_hour()
    chart.compile_hr_min_time()
    chart.compile_iso_date()
    read_file_iterator = chart.read_file()
    ruler_line = chart.create_ruler()
    print(ruler_line, file=chart.outfile)
    chart.make_output(read_file_iterator)
    if chart.outfile:
        del chart.outfile
    logging.info('chart finish')


def get_parse_args():
    """
    Parse and return the c.l.a.'s

    Called by: main()
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--infilename', default=None,
                        help='the input file name')
    parser.add_argument('-o', '--outfilename', default=None,
                        help='the output file name')
    parser.add_argument('-d', '--debug',
                        help=("output X, o, - instead of '\u2588', '\u0020', "
                              "'\u2591'"), action='store_true')
    return parser.parse_args()


if __name__ == '__main__':
    main()
