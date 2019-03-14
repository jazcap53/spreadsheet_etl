# file: chart.py
# andrew jarcho
# 10/2018


from tests.file_access_wrappers import FileReadAccessWrapper
import re
import sys
from datetime import datetime, timedelta, date
import copy


class Chart:
    """
    Create a sleep chart from input data
    """
    ASLEEP = u'\u2588'   # the printed color (black ink)
    AWAKE = u'\u0020'    # the background color (white paper)
    UNKNOWN = u'\u2591'  # no data

    QS_IN_DAY = 96  # 24 * 4

    hours = []
    for h in range(24):
        hours.extend([str(h).zfill(2)] * 4)
    minutes = [str(m).zfill(2) for m in range(0, 60, 15)] * 24
    intervals = list(map(lambda h, m: h + ':' + m + ':00', hours, minutes))
    positions = list(range(96))
    intervals_to_positions = dict(list(zip(intervals, positions)))

    def __init__(self, filename):
        self.filename = filename
        self.infile = None
        self.cur_line = ''
        self.prev_line = ''
        self.sleep_state = self.AWAKE
        self.date_re = None
        self.cur_date_str = ''
        self.cur_time_str = ''
        self.cur_date_time_str = ''
        self.cur_date = None
        self.cur_time = None
        self.cur_datetime = None
        self.cur_interval = None
        self.qs_carried = 0
        self.day_row = [Chart.UNKNOWN] * Chart.QS_IN_DAY
        self.header_seen = False
        self.start_from_0 = False

    def get_a_line(self):
        """

        :return: bool
        Called by: read_file()
        """
        self.cur_line = self.infile.readline().rstrip()
        if not self.header_seen:
            self.skip_header()
        return bool(self.cur_line)

    def skip_header(self):
        while self.cur_line and not self.date_re.match(self.cur_line):
            self.cur_line = self.infile.readline().rstrip()
        self.header_seen = True

    def read_file(self):
        """
        Send each line of file to parser.

        :yield: a parsed input line
        :return: None
        Called by: main()
        """
        with open(self.filename) as self.infile:
            while self.get_a_line():
                parsed_input_line = self.parse_input_line()  # gets a 3-tuple
                if all(parsed_input_line):
                    # self.cur_datetime, self.cur_interval = parsed_input_line
                    # yield self.interval_str_to_int()
                    yield parsed_input_line

    def parse_input_line(self):
        """
        Parse a line of input.

        :return: my_date, a datetime.date object
                 my_time, an int (the offset into a copy of self.my_day_row)
                 my_interval, an int (the number of 1/4 hrs in interval)
        """
        line_array = self.cur_line.split('|')  # cur_line[-1] may be '|'
        line_array = list(map(str.strip, line_array))  # so strip() now
        if len(line_array) < 2:
            return None, None, None
        date_str = line_array[0]
        time_str = line_array[1]
        interval_str = line_array[2]
        my_date = date.fromisoformat(date_str)
        my_time = self.time_or_interval_str_to_int(time_str)
        my_interval = self.time_or_interval_str_to_int(interval_str)

        # date_time_str = date_str + ((' ' + time_str) if time_str else '')
        # my_datetime = datetime.strptime(date_time_str,
        #                                 ('%Y-%m-%d %H:%M:%S' if
        #                                  time_str else '%Y-%m-%d'))
        # my_interval = timedelta(hours=int(interval[:2]), minutes=int(interval[3:5]))

        return my_date, my_time, my_interval

    def make_output_line(self, read_file_iterator):
        """
        
        1) Output any quarters left over from previous line.

        :return:
        Called by: main()
        """
        # read_file_iterator = self.read_file()
        my_day_row = self.day_row[:]
        offset = 0
        my_date, my_time, my_interval = next(read_file_iterator)
        while self.qs_carried:  # 1) set first self.qs_carried qs to Chart.ASLEEP
            my_day_row[offset] = self.ASLEEP
            offset += 1
            self.qs_carried -= 1
        # while offset < Chart.QS_IN_DAY:  # while some qs are unset
        while True:
            # my_date, my_time, my_interval = next(read_file_iterator)
            while offset < my_time:
                my_day_row[offset] = self.AWAKE
                offset += 1
            while offset < my_time + my_interval:
                my_day_row[offset] = self.ASLEEP
                offset += 1
                if offset == Chart.QS_IN_DAY:
                    self.qs_carried = my_time + my_interval - offset
                    # break
                    joined_row = ''.join(my_day_row)
                    return f'{my_date}: {joined_row}'
            my_date, my_time, my_interval = next(read_file_iterator)

    def handle_quarters_carried(self):
        self.cur_datetime += timedelta(days=1)
        my_day_row = self.day_row[:]
        for i in range(self.quarters_carried):
            my_day_row[i] = Chart.ASLEEP
        self.quarters_carried = 0

    def time_or_interval_str_to_int(self, my_str):
        """
        Obtain from self.cur_interval the number of 15-minute chunks it contains
        :return: int: the number of chunks
        Called by: read_file()
        """
        if my_str:
            return int(my_str[:2]) * 4 + \
                   int(my_str[3:5]) // 15
        else:
            return 0

    def compile_date_re(self):
        """
        :return: None
        Called by: main()
        """
        self.date_re = re.compile(r' \d{4}-\d{2}-\d{2} \|')


def main():
    chart = Chart('/home/jazcap53/python_projects/spreadsheet_etl/src/chart/chart_raw_data_new.txt')
    chart.compile_date_re()
    read_file_iterator = chart.read_file()
    lines_printed = 0
    ruler = ''.join(list(map(lambda x: str(x) + ' | ', range(10)))) + \
        '0 | 1 | '
    ruler_line = ' ' * 12 + ruler * 2

    while True:
        if not lines_printed % 7:
            print(ruler_line)
        try:
            print(chart.make_output_line(read_file_iterator))
            lines_printed += 1
        except StopIteration:
            break


if __name__ == '__main__':
    main()


# NOTES
# >>> import datetime
# >>> my_date = '2016-12-07'
# >>> my_time = '23:45:00'
# >>> my_datetime = my_date + ' ' + my_time
# >>> my_datetime
# '2016-12-07 23:45:00'
# >>> my_date_and_time = my_date + ' ' + my_time
# >>> my_datetime = datetime.datetime.strptime(my_date_and_time, '%Y-%m-%d %H:%M:%S')
# >>> my_datetime
# datetime.datetime(2016, 12, 7, 23, 45)
# >>> my_newer_datetime = my_datetime + datetime.timedelta(minutes=15)
# >>> my_newer_datetime
# datetime.datetime(2016, 12, 8, 0, 0)
