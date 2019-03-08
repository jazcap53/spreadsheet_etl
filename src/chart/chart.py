# file: chart.py
# andrew jarcho
# 10/2018


from tests.file_access_wrappers import FileReadAccessWrapper
import re
import sys
from datetime import datetime, timedelta
import copy


class Chart:
    """
    Create a sleep chart from input data
    """
    ASLEEP = u'\u2588'  # the printed color (black ink)
    AWAKE = u'\u0020'   # the background color (white paper)

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
        self.quarters_carried = 0
        self.day_row = [Chart.AWAKE] * 24 * 4
        self.header_seen = False

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
        :return: None
        Called by: main()
        """
        with open(self.filename) as self.infile:
            while self.get_a_line():
                parsed_input_line = self.parse_input_line()  # gets a 2-tuple
                if all(parsed_input_line):
                    self.cur_datetime, self.cur_interval = parsed_input_line
                    yield self.interval_str_to_int()

    def parse_input_line(self):
        line_array = self.cur_line.split('|')  # cur_line[-1] may be '|'
        line_array = list(map(str.strip, line_array))  # so strip() now
        if len(line_array) < 2:
            return None, None, None
        date_str = line_array[0].strip()
        time_str = line_array[1].strip()
        interval = line_array[2].strip()
        date_time_str = date_str + ((' ' + time_str) if time_str else '')
        my_datetime = datetime.strptime(date_time_str,
                                        ('%Y-%m-%d %H:%M:%S' if
                                         time_str else '%Y-%m-%d'))
        # my_interval = timedelta(hours=int(interval[:2]), minutes=int(interval[3:5]))
        return my_datetime, interval

    def make_output_line(self, quarters_count):
        my_date = self.cur_datetime.strftime('%b %d, %Y')
        if self.quarters_carried:
            print(f'{self.quarters_carried} quarters carried on date {my_date}')
            self.handle_quarters_carried(my_date)
        my_cur_datetime_copy = copy.copy(self.cur_datetime)
        my_interval = self.cur_interval
        my_start_time = self.cur_datetime.strftime('%H:%M:%S')
        my_day_row = self.day_row[:]
        my_day_row_offset = Chart.intervals_to_positions[my_interval]
        # my_day_row[Chart.intervals_to_positions[my_interval]] = Chart.ASLEEP
        my_day_row[my_day_row_offset] = Chart.ASLEEP
        quarters_count -= 1
        while quarters_count and my_day_row_offset < 24 * 4:
            my_day_row_offset += 1
            quarters_count -= 1
            my_day_row[my_day_row_offset] = Chart.ASLEEP


        # my_interval += timedelta(minutes=15)

        my_output_line = my_date + ': |' + "".join(my_day_row) + '|'
        return my_output_line

    def handle_quarters_carried(self, my_date):
        self.quarters_carried = 0  # TODO: N.Y.I.

    def interval_str_to_int(self):
        """
        Obtain from self.cur_interval the number of 15-minute chunks it contains
        :return: int: the number of chunks
        Called by: read_file()
        """
        if self.cur_interval:
            return int(self.cur_interval[:2]) * 4 + \
                   int(self.cur_interval[3:5]) // 15

    def compile_date_re(self):
        """
        :return: None
        Called by: main()
        """
        self.date_re = re.compile(r' \d{4}-\d{2}-\d{2} \|')


def main():
    chart = Chart('/home/jazcap53/python_projects/spreadsheet_etl/src/chart/chart_raw_data.txt')
    chart.compile_date_re()
    read_file_iterator = chart.read_file()
    while True:
        try:
            print(chart.make_output_line(next(read_file_iterator)))
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
