# file: chart.py
# andrew jarcho
# 10/2018


from tests.file_access_wrappers import FileReadAccessWrapper
import re
import sys
from datetime import datetime, timedelta, date
import copy
from collections import namedtuple


Triple = namedtuple('Triple', ['start', 'finish', 'symbol'], defaults=[0, 0, 0])


class Chart:
    """
    Create a sleep chart from input data
    """
    ASLEEP = u'\u2588'   # the printed color (black ink)
    AWAKE = u'\u0020'    # the background color (white paper)
    UNKNOWN = u'\u2591'  # no data

    QS_IN_DAY = 96  # 24 * 4

    # Triple = namedtuple('Triple', ['start', 'finish', 'symbol'], defaults=[0, 0, 0])

    # hours = []
    # for h in range(24):
    #     hours.extend([str(h).zfill(2)] * 4)
    # minutes = [str(m).zfill(2) for m in range(0, 60, 15)] * 24
    # intervals = list(map(lambda h, m: h + ':' + m + ':00', hours, minutes))
    # positions = list(range(96))
    # intervals_to_positions = dict(list(zip(intervals, positions)))

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
        self.cur_day_row = []
        self.header_seen = False
        self.start_from_0 = False

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
                yield parsed_input_line

    def get_a_line(self):
        """
        Get next non-header, non-date-only input line

        :return: bool
        Called by: read_file()
        """
        self.cur_line = self.infile.readline().rstrip()
        if not self.header_seen:
            self.skip_header()
        while self.cur_line[14:22] == ' ' * 8:
            self.cur_line = self.infile.readline().rstrip()
        return bool(self.cur_line)

    def skip_header(self):
        """
        Skip the file's header lines

        :return:
        Called by: get_a_line()
        """
        while self.cur_line and not self.date_re.match(self.cur_line):
            self.cur_line = self.infile.readline().rstrip()
        self.header_seen = True

    def parse_input_line(self):
        """

        :return: a Triple holding
                     a start position,
                     a one-past-end position,
                     a unicode character (ASLEEP, AWAKE, UNKNOWN)
        Called by: read_file()
        """
        line_array = self.cur_line.split('|')  # cur_line[-1] may be '|'
        line_array = list(map(str.strip, line_array))  # so strip() now
        if len(line_array) < 2:
            return Triple(None, None, None)
        start = self.time_or_interval_str_to_int(line_array[1])
        finish = start + self.time_or_interval_str_to_int(line_array[2])
        symbol = self.ASLEEP
        # my_triple = Triple(start, finish, symbol)
        return Triple(start, finish, symbol)

    def make_output(self, read_file_iterator):
        """

        Make new day row.
        Insert any left over quarters to new day row.

        :return:
        Called by: main()
        """
        self.cur_day_row = self.day_row[:]
        my_triple = Triple(0, 0, self.AWAKE)

        if self.qs_carried:
            carried_triple = Triple(0, self.qs_carried, self.ASLEEP)
            self.insert_to_day_row(carried_triple)
        else:
            carried_triple = Triple(0, 0, 0)

        my_start, my_finish, my_symbol = next(read_file_iterator)  # yielded from read_file()
        my_triple = Triple(my_start, my_finish, my_symbol)
        if carried_triple.finish < my_start:
            self.insert_to_day_row(Triple(carried_triple.finish, my_triple.start, self.AWAKE))



        self.insert_to_day_row(my_triple)

        print(''.join(self.cur_day_row))

    def insert_to_day_row(self, triple):
        for i in range(triple.start, triple.finish):
            self.cur_day_row[i] = triple.symbol


    def handle_qs_carried(self, my_day_row, offset):
        while self.qs_carried:
            my_day_row[offset] = self.ASLEEP
            offset += 1
            self.qs_carried -= 1
        return my_day_row, offset

    def time_or_interval_str_to_int(self, my_str):
        """
        Obtain from self.cur_interval the number of 15-minute chunks it contains
        :return: int: the number of chunks
        Called by: read_file()
        """
        if my_str:
            return (int(my_str[:2]) * 4 +
                    int(my_str[3:5]) // 15) % (24 * 4)
        else:
            return 0

    def compile_date_re(self):
        """
        :return: None
        Called by: main()
        """
        self.date_re = re.compile(r' \d{4}-\d{2}-\d{2} \|')

    @staticmethod
    def create_ruler():
        ruler = list(str(x) for x in range(12)) * 2
        for ix, val in enumerate(ruler):
            if ix == 0:
                ruler[ix] = '12a'
            elif ix == 12:
                ruler[ix] = '12p'

        ruler_line = ' ' * 12 + ''.join(v.ljust(5, ' ') for v in ruler)
        return ruler_line


def main():
    chart = Chart('/home/jazcap53/python_projects/spreadsheet_etl/src/chart/chart_raw_data_new.txt')
    chart.compile_date_re()
    read_file_iterator = chart.read_file()
    lines_printed = 0
    ruler_line = chart.create_ruler()

    while True:
        if not lines_printed % 7:
            print(ruler_line)
        try:
            print(chart.make_output(read_file_iterator))
            lines_printed += 1
        except StopIteration:
            break


if __name__ == '__main__':
    main()
