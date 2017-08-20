#!/usr/bin/python3


# file: src/transform/do_transform_class.py
# andrew jarcho
# 2017-03-16


"""
Read lines from stdin, transform to a db_s_etl-friendly format, and write to stdout.

The output will be usable by the database with a minimum of further
processing, and will hold all relevant data from the input.
"""

import fileinput
import logging
import logging.handlers


class Transform:

    def __init__(self, data_source=fileinput):
        """
        The data source will be a file or FakeFileReadWrapper object
        if either is passed as a ctor argument. Otherwise the
        data source will be stdin, which is tied to stdout from the
        'extract' phase subprocess.
        """
        self.data_source = data_source
        self.out_val = None
        self.last_date = ''
        self.last_sleep_time = ''

    def read_each_line(self):
        """
        Read a line at a time from data_source; write to stdout.

        Not necessary to filter input as it's coming directly from
        extract process stdout:
        https://docs.python.org/3/library/subprocess.html#security-considerations

        Called by: __main__()
        """
        with self.data_source.input() as infile:
            for curr_line in infile:
                self.process_curr(curr_line.rstrip('\n'))

    def process_curr(self, cur_l):
        """
        Process a single line of input.
        Called by: read_each_line()

        Takes a string argument, and may output a single line
        to stdout. The output may depend on values from previous input strings,
        as well as on values in the current input string. Output is formatted
        as:
           'NIGHT, date, time'  or
           'NAP, time, duration'
        Returns: None
        """
        if cur_l == '':
            pass
        elif cur_l[0] == 'W':  # 'Week of ...'
            pass
        elif cur_l[0] == '=':  # '========...'
            pass
        elif cur_l[0] == ' ':  # a date in the format '    yyyy-mm-dd'
            self.last_date = cur_l[4:]
        elif cur_l[: 9] == 'action: b':
            self.last_sleep_time = self.get_wake_or_last_sleep(cur_l)
            self.out_val = 'NIGHT, {}, {}'.format(self.last_date, self.last_sleep_time)
        elif cur_l[: 9] == 'action: s':
            self.last_sleep_time = self.get_wake_or_last_sleep(cur_l)
        elif cur_l[: 9] == 'action: w':
            wake_time = self.get_wake_or_last_sleep(cur_l)
            duration = self.get_duration(wake_time, self.last_sleep_time)
            self.out_val = 'NAP, {}, {}'.format(self.last_sleep_time, duration)
        else:
            print('BAD VALUE {} in input'.format(cur_l))
            raise IndexError
        if self.out_val is not None:
            print(self.out_val)
        self.out_val = None

    @staticmethod
    def get_wake_or_last_sleep(cur_l):
        """
        Extract and return the time part of its string argument.

        Input time may be in 'h:mm' or 'hh:mm' format.
        Called by: process_curr().
        Returns: Extracted time as a string in 'hh:mm' format.
        """
        end_pos = cur_l.rfind(', hours: ')
        out_time = cur_l[17:] if end_pos == -1 else cur_l[17: end_pos]
        if len(out_time) == 4:
            out_time = '0' + out_time
        return out_time

    @staticmethod
    def get_duration(w_time, s_time):
        """
        Calculate the interval between w_time and s_time.

        Arguments are strings representing times in 'hh:mm' format.
        get_duration() calculates the interval between them as a
        string in decimal format e.g.,
            04.25 for 4 1/4 hours
        Called by: process_curr()
        Returns: the calculated interval, whose value will be
                non-negative.
        """
        w_time_list = list(map(int, w_time.split(':')))
        s_time_list = list(map(int, s_time.split(':')))
        if w_time_list[1] < s_time_list[1]:  # wake minit < sleep minit
            w_time_list[1] += 60
            w_time_list[0] -= 1
        if w_time_list[0] < s_time_list[0]:  # wake hour < sleep hour
            w_time_list[0] += 24
        dur_list = [(w_time_list[x] - s_time_list[x]) for x in range(len(w_time_list))]
        duration = str(dur_list[0])
        if len(duration) == 1:  # change hour from '1' to '01', e.g.
            duration = '0' + duration
        duration += Transform.quarter_hour_to_decimal(s_time_list[1])
        return duration

    @staticmethod
    def quarter_hour_to_decimal(quarter):
        """
        Convert an integer number of minutes into a decimal string

        Argument is a number of minutes past the hour. If that number
        is a quarter-hour, convert it to a decimal quarter represented
        as a string.

        Called by: get_duration()
        Returns: a number of minutes represented as a decimal fraction
        """
        # TODO: log warning if quarter is not a quarter-hour
        decimal_quarter = None
        if quarter == 15:
            decimal_quarter = '.25'
        elif quarter == 30:
            decimal_quarter = '.50'
        elif quarter == 45:
            decimal_quarter = '.75'
        elif quarter == 0:
            decimal_quarter = '.00'
        return decimal_quarter


def main():
    # from: https://docs.python.org/3/howto/logging-cookbook.html#network-logging
    rootLogger = logging.getLogger('')
    rootLogger.setLevel(logging.INFO)
    socketHandler = logging.handlers.SocketHandler('localhost',
            logging.handlers.DEFAULT_TCP_LOGGING_PORT)
    # don't bother with a formatter, since a socket handler sends the event as
    # an unformatted pickle
    rootLogger.addHandler(socketHandler)


if __name__ == '__main__':
    main()
    logging.info('transform class start')
    t = Transform()
    t.read_each_line()
    logging.info('transform class finish')
