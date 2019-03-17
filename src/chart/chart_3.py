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
        self.current_line = ''
        self.prev_line = ''
        self.sleep_state = self.AWAKE
        self.date_re = None
        self.current_date_str = ''
        self.current_time_str = ''
        self.current_date_time_str = ''
        self.current_date = None
        self.current_time = None
        self.current_datetime = None
        self.current_interval = None
        self.quarters_carried = 0
        self.output_row = [Chart.UNKNOWN] * Chart.QS_IN_DAY
        self.current_output_row = []
        self.header_seen = False
        self.start_from_0 = False
        self.spaces_left = 24 * 4

    def read_file(self):
        """
        Send each line of file to parser.

        :yield: a parsed input line
        :return: None
        Called by: main()
        """
        with open(self.filename) as self.infile:
            while self.get_a_line():
                parsed_input_line = self.parse_input_line()  # gets a Triple
                yield parsed_input_line

    def get_a_line(self):
        """
        Get next non-header, non-date-only input line

        :return: bool
        Called by: read_file()
        """
        self.current_line = self.infile.readline().rstrip()
        if not self.header_seen:
            self.skip_header()
        while self.current_line[14:22] == ' ' * 8:
            self.current_line = self.infile.readline().rstrip()
        return bool(self.current_line)

    def skip_header(self):
        """
        Skip the file's header lines

        :return:
        Called by: get_a_line()
        """
        while self.current_line and not self.date_re.match(self.current_line):
            self.current_line = self.infile.readline().rstrip()
        self.header_seen = True

    def parse_input_line(self):
        """

        :return: a Triple holding
                     a start position,
                     a one-past-end position,
                     a unicode character (ASLEEP, AWAKE, UNKNOWN)
        Called by: read_file()
        """
        line_array = self.current_line.split('|')  # current_line[-1] may be '|'
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
        self.current_output_row = self.output_row[:]
        self.spaces_left = 24 * 4
        
        while True:
            if self.quarters_carried:
                carried_triple = Triple(0, self.quarters_carried, self.ASLEEP)
                self.insert_to_output_row(carried_triple)
                self.quarters_carried = 0
            else:
                carried_triple = Triple(0, 24 * 4, self.UNKNOWN)
            try:
                current_triple = Triple(*next(read_file_iterator))  # yielded from read_file()
                if current_triple.start is None:
                    return
            except RuntimeError:
                return
            len_segment = current_triple.finish - current_triple.start
            # fill gap between carried and current triples
            # if carried_triple.finish < current_triple.start:
            spaces_used = self.get_spaces_used()
            if spaces_used < current_triple.start:
                self.insert_to_output_row(Triple(spaces_used,
                                          current_triple.start, self.AWAKE))
            if len_segment < self.spaces_left:
                self.insert_to_output_row(current_triple)
            elif len_segment == self.spaces_left:
                self.insert_to_output_row(current_triple)
                # print(''.join(self.current_output_row))
                self.output(self.current_output_row)
                self.current_output_row = self.output_row[:]
                self.spaces_left = 24 * 4
            else:
                self.insert_to_output_row(current_triple)
                # print(''.join(self.current_output_row))
                self.output(self.current_output_row)
                self.current_output_row = self.output_row[:]
                self.spaces_left = 24 * 4



    def insert_to_output_row(self, triple):
        if triple.finish > 24 * 4:
            self.quarters_carried = triple.finish - 24 * 4
            triple = triple._replace(finish=24 * 4)

        for i in range(triple.start, triple.finish):
            self.current_output_row[i] = triple.symbol
            self.spaces_left -= 1
        # self.spaces_left -= triple.finish - triple.start
        # if self.spaces_left < 0:
        #     self.spaces_left =

    def get_spaces_used(self):
        return 24 * 4 - self.spaces_left

    def output(self, my_output_row):
        extended_output_row = []
        for ix, val in enumerate(my_output_row):
            if ix and not ix % 4 and ix != 24 * 4:
                extended_output_row.extend(['|', val])
            else:
                extended_output_row.append(val)
        print('01-01-2001: ' + ''.join(extended_output_row))



    def handle_quarters_carried(self, my_output_row, offset):
        while self.quarters_carried:
            my_output_row[offset] = self.ASLEEP
            offset += 1
            self.quarters_carried -= 1
        return my_output_row, offset

    def time_or_interval_str_to_int(self, my_str):
        """
        Obtain from self.current_interval the number of 15-minute chunks it contains
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
            chart.make_output(read_file_iterator)
            output_line = ''.join(chart.current_output_row)
            print(output_line)
            lines_printed += 1
        except StopIteration:
            break


if __name__ == '__main__':
    main()

'''
spaces_used = self.get_spaces_used()
if spaces_used < current_triple.start:
    self.insert_to_output_row(Triple(spaces_used,
                                     current_triple.start, self.AWAKE))
'''