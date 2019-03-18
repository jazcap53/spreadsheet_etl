# file: chart.py
# andrew jarcho
# 10/2018


from tests.file_access_wrappers import FileReadAccessWrapper
import re
from datetime import datetime, timedelta
from collections import namedtuple


Triple = namedtuple('Triple', ['start', 'length', 'symbol'], defaults=[0, 0, 0])
QS_IN_DAY = 96  # 24 * 4
ASLEEP = u'\u2588'  # the printed color (black ink)
AWAKE = u'\u0020'  # the background color (white paper)
UNKNOWN = u'\u2591'  # no data


class Chart:
    """
    Create a sleep chart from input data
    """
    def __init__(self, filename):
        self.filename = filename
        self.infile = None
        self.current_line = ''
        self.prev_line = ''
        self.sleep_state = AWAKE
        self.date_re = None
        self.quarters_carried = 0
        self.output_row = [UNKNOWN] * QS_IN_DAY
        self.current_output_row = []
        self.header_seen = False
        self.spaces_left = QS_IN_DAY
        self.current_date = '2016-12-06'

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
                     a count of quarter hours,
                     a unicode character (ASLEEP, AWAKE, UNKNOWN)
        Called by: read_file()
        """
        line_array = self.current_line.split('|')  # current_line[-1] may be '|'
        line_array = list(map(str.strip, line_array))  # so strip() now
        if len(line_array) < 2:
            return Triple(None, None, None)
        start = self.time_or_interval_str_to_int(line_array[1])
        length = self.time_or_interval_str_to_int(line_array[2])
        symbol = ASLEEP
        return Triple(start, length, symbol)

    def make_output(self, read_file_iterator):
        """

        Make new day row.
        Insert any left over quarters to new day row.

        :return:
        Called by: main()
        """
        self.current_output_row = self.output_row[:]
        self.spaces_left = QS_IN_DAY
        
        while True:
            try:
                current_triple = Triple(*next(read_file_iterator))  # yielded from read_file()
                if current_triple.start is None:
                    return
            except RuntimeError:
                return
            len_segment = current_triple.length
            current_position = self.get_current_position()
            if current_position < current_triple.start:
                self.insert_to_output_row(Triple(current_position,
                                          current_triple.start - current_position, AWAKE))
            else:
                self.insert_to_output_row(Triple(current_position, QS_IN_DAY - current_position, AWAKE))
                self.write_output(self.current_output_row)
                self.current_output_row = self.output_row[:]
                self.spaces_left = QS_IN_DAY
                if current_triple.start > 0:
                    self.insert_to_output_row(Triple(0, current_triple.start, AWAKE))
            if len_segment < self.spaces_left:
                self.insert_to_output_row(current_triple)
            elif len_segment == self.spaces_left:
                self.insert_to_output_row(current_triple)
                self.write_output(self.current_output_row)
                self.current_output_row = self.output_row[:]
                self.spaces_left = QS_IN_DAY
            else:
                self.insert_to_output_row(current_triple)
                self.write_output(self.current_output_row)
                self.current_output_row = self.output_row[:]
                self.spaces_left = QS_IN_DAY
            if self.quarters_carried:
                self.handle_quarters_carried()

    def handle_quarters_carried(self):
        self.insert_to_output_row(Triple(0, self.quarters_carried, ASLEEP))
        self.quarters_carried = 0

    def insert_to_output_row(self, triple):
        finish = triple.start + triple.length
        if finish > QS_IN_DAY:
            self.quarters_carried = finish - QS_IN_DAY
            triple = triple._replace(length=triple.length - self.quarters_carried)

        for i in range(triple.start, triple.start + triple.length):
            self.current_output_row[i] = triple.symbol
            self.spaces_left -= 1

    def get_current_position(self):
        return QS_IN_DAY - self.spaces_left

    def write_output(self, my_output_row):
        extended_output_row = []
        for ix, val in enumerate(my_output_row):
            extended_output_row.append(val)
        self.advance_date()
        print(f'{self.current_date} |{"".join(extended_output_row)}|')

    def advance_date(self):
        date_as_datetime = datetime.strptime(self.current_date, '%Y-%m-%d')
        if date_as_datetime.date().weekday() == 5:
            print(self.create_ruler())
        date_as_datetime += timedelta(days=1)
        self.current_date = date_as_datetime.strftime('%Y-%m-%d')

    @staticmethod
    def time_or_interval_str_to_int(my_str):
        """
        Obtain from self.current_interval the number of 15-minute chunks it contains
        :return: int: the number of chunks
        Called by: read_file()
        """
        if my_str:
            return (int(my_str[:2]) * 4 +
                    int(my_str[3:5]) // 15) % QS_IN_DAY
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
        ruler_line = ' ' * 12 + ''.join(v.ljust(4, ' ') for v in ruler)
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
