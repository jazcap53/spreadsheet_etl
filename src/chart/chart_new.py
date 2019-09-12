# file: chart.py
# andrew jarcho
# 10/2018


from tests.file_access_wrappers import FileReadAccessWrapper
import sys  # temporary: for sys.exit()
import re
from datetime import datetime, timedelta
from collections import namedtuple


Triple = namedtuple('Triple', ['start', 'length', 'symbol'], defaults=[0, 0, 0])
QS_IN_DAY = 96  # 24 * 4 quarter hours in a day
ASLEEP = u'\u2588'  # the printed color (black ink)
AWAKE = u'\u0020'  # the background color (white paper)
NO_DATA = u'\u2591'  # no data


class Chart:
    """
    Create a sleep chart from input data
    """
    def __init__(self, filename):
        self.filename = filename
        self.infile = None
        self.curr_line = ''
        self.prev_line = ''
        self.sleep_state = NO_DATA  # TODO: was AWAKE
        self.date_re = None
        self.quarters_carried = 0
        self.output_row = [NO_DATA] * QS_IN_DAY
        # self.header_seen = False
        self.spaces_left = QS_IN_DAY
        self.input_date = ''
        self.output_date = '2016-12-06'
        self.date_advanced = 0
        self.curr_sunday = ''
        self.date_in = None

    def read_file(self):
        """
        Send each line of file to parser.

        :yield: a parsed input line
        :return: None
        Called by: main()
        """
        with open(self.filename) as self.infile:
            ctr = 0
            while self.get_a_line() and ctr < 100:
                self.input_date, parsed_input_line = self.parse_input_line()
                yield parsed_input_line  # parsed_input_line is a Triple
                ctr += 1

    def get_a_line(self):
        """
        Get next input line, discarding blank lines and '======'s

        :return: bool
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

    def parse_input_line(self):
        """

        :return: a date, and a Triple holding
                     a start position,
                     a count of quarter hours,
                     a unicode character (ASLEEP, AWAKE, NO_DATA)
        Called by: read_file()
        """
        line_array = self.curr_line.split(',')
        if len(line_array) == 1:
            self.date_in = line_array[0]  # TODO: should date_in be a data member?
            return self.date_in, Triple(0, 8, NO_DATA)
        else:  # len(line_array) == 2:
            # TODO: duration must come from line_array[2] of subsequent line, or from
            #       a wake:sleep interval
            duration = 0
            action = line_array[0][-1]
            act_time = self.get_time_part_from(self.curr_line)
            start = self.get_num_chunks(line_array[1])  # TODO: get start posn from line_array[1]
            if len(line_array) > 2:
                duration = self.get_num_chunks(line_array[2])

        # TODO: write a self.set_symbol(line_array) function -- call it
        #       wherever a symbol must be output (???) OR call it below only (???)

            symbol = ASLEEP
            print(self.date_in, Triple(start, duration, symbol))
            return '2019-09-12', Triple(0, 4, symbol)



    def handle_action_line(self, line):
        if line.startswith('action: b'):
            self.last_sleep_time = self.get_time_part_from(line)
            self.out_val = 'NIGHT, {}, {}, {}, {}'.format(self.last_date,
                                                          self.last_sleep_time,
                                                          'false', 'false')
        elif line.startswith('action: s'):
            self.last_sleep_time = self.get_time_part_from(line)
        elif line.startswith('action: w'):
            wake_time = self.get_time_part_from(line)
            duration = self.get_duration(wake_time, self.last_sleep_time)
            self.out_val = 'NAP, {}, {}'.format(self.last_sleep_time, duration)
        elif line.startswith('action: N'):
            self.last_sleep_time = self.get_time_part_from(line)
            self.out_val = 'NIGHT, {}, {}, {}, {}'.format(self.last_date,
                                                          self.last_sleep_time,
                                                          'true', 'false')
        elif line.startswith('action: Y'):
            self.last_sleep_time = self.get_time_part_from(line)
            self.out_val = 'NIGHT, {}, {}, {}, {}'.format(self.last_date,
                                                          self.last_sleep_time,
                                                          'false', 'true')

    @staticmethod
    def get_time_part_from(cur_l):
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





    def make_output(self, read_file_iterator):
        """

        Make new day row.
        Insert any left over quarters to new day row.

        :return:
        Called by: main()
        """
        row_out = self.output_row[:]
        self.spaces_left = QS_IN_DAY
        
        while True:
            try:
                curr_triple = next(read_file_iterator)
                if curr_triple.start is None:  # reached end of input
                    return
            except StopIteration:
                return

            row_out = self.write_leading_blanks(curr_triple, row_out)
            spaces_left_now = self.spaces_left
            row_out = self.insert_to_row_out(curr_triple, row_out)
            if curr_triple.length >= spaces_left_now:
                self.write_output(row_out)  # TODO: ADVANCES self.output_date
                row_out = self.output_row[:]  # get fresh copy of row to output
                self.spaces_left = QS_IN_DAY
            if self.quarters_carried:
                row_out = self.handle_quarters_carried(row_out)

    def write_leading_blanks(self, curr_triple, row_out):
        """
        Write blanks onto row_out from current posn to start of curr_triple.
        :param curr_triple:
        :param row_out:
        :return:
        Called by: make_output()
        """
        curr_posn = QS_IN_DAY - self.spaces_left
        if curr_posn < curr_triple.start:
            triple_to_insert = Triple(curr_posn,
                                      curr_triple.start - curr_posn, AWAKE)
            row_out = self.insert_to_row_out(triple_to_insert, row_out)
        else:
            triple_to_insert = Triple(curr_posn,
                                      QS_IN_DAY - curr_posn, AWAKE)
            row_out = self.insert_to_row_out(triple_to_insert, row_out)
            self.write_output(row_out)
            row_out = self.output_row[:]
            self.spaces_left = QS_IN_DAY
            if curr_triple.start > 0:
                triple_to_insert = Triple(0, curr_triple.start, AWAKE)
                row_out = self.insert_to_row_out(triple_to_insert, row_out)
        return row_out

    def handle_quarters_carried(self, curr_output_row):
        curr_output_row = self.insert_to_row_out(
                Triple(0, self.quarters_carried, ASLEEP), curr_output_row)
        self.quarters_carried = 0
        return curr_output_row

    def insert_to_row_out(self, triple, output_row):
        finish = triple.start + triple.length
        if finish > QS_IN_DAY:
            self.quarters_carried = finish - QS_IN_DAY
            triple = triple._replace(length=triple.length - self.quarters_carried)
        for i in range(triple.start, triple.start + triple.length):
            output_row[i] = triple.symbol
            self.spaces_left -= 1
        return output_row

    def get_curr_posn(self):
        return QS_IN_DAY - self.spaces_left

    def write_output(self, my_output_row):
        """

        :param my_output_row:
        :return:
        Called by: make_output()
        """
        extended_output_row = []
        for ix, val in enumerate(my_output_row):
            extended_output_row.append(val)
        self.output_date = self.advance_output_date(self.output_date)
        print(f'{self.output_date} |{"".join(extended_output_row)}|')

    def advance_date(self, my_date, make_ruler=False):
        date_as_datetime = datetime.strptime(my_date, '%Y-%m-%d')
        if make_ruler and date_as_datetime.date().weekday() == 5:
            print(self.create_ruler())
        date_as_datetime += timedelta(days=1)
        return date_as_datetime.strftime('%Y-%m-%d')

    def advance_input_date(self, my_input_date):
        return self.advance_date(my_input_date)

    def advance_output_date(self, my_output_date):
        return self.advance_date(my_output_date, True)

    @staticmethod
    def get_num_chunks(my_str):
        """
        Obtain from self.curr_interval the number of 15-minute chunks it contains
        :return: int: the number of chunks
        Called by: read_file()
        """
        if my_str:
            m = re.search(r'(\d{1,2})(?:\.|:)(\d{2})', my_str)  # TODO: compile this
            return (int(m.group(1)) * 4 +  # 4 chunks per hour
                    int(m.group(2)) // 15) % QS_IN_DAY
            # return (int(my_str[:2]) * 4 +  # 4 chunks per hour
            #         int(my_str[3:5]) // 15) % QS_IN_DAY
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
    chart = Chart('/home/jazcap53/python_projects/spreadsheet_etl/' +
                  'xtraneous/transform_input_2019-09-01_v3.txt')
    chart.compile_date_re()
    read_file_iterator = chart.read_file()
    ruler_line = chart.create_ruler()
    print(ruler_line)
    chart.make_output(read_file_iterator)


if __name__ == '__main__':
    main()
