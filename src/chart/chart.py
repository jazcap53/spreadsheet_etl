# file: chart.py
# andrew jarcho
# 10/2018


from tests.file_access_wrappers import FileReadAccessWrapper
import re
import sys
from datetime import datetime


class Chart:
    """
    Create a sleep chart from input data
    """
    ASLEEP = 1  # the printed color (black ink)
    AWAKE = 0   # the background color (white paper)

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
        self.cur_nap_id = 0
        self.days_carried = 0
        self.day_row = [self.AWAKE] * 24 * 4
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
                parsed_line = self.parse_line()  # a 2-tuple
                if any(parsed_line):
                    self.cur_datetime, self.cur_interval = parsed_line
                    print(self.cur_datetime, self.cur_interval,
                          sep='   ')

    def parse_line(self):
        line_array = self.cur_line.split('|')  # cur_line[-1] may be '|'
        line_array = list(map(str.strip, line_array))  # so strip() now
        if len(line_array) < 2:
            return None, None, None
        # nap_id = 0
        date_str = line_array[0].strip()
        time_str = line_array[1].strip()
        interval = line_array[2].strip()
        # if line_array[3]:
        #     nap_id = int(line_array[3].strip())
        date_time_str = date_str + ((' ' + time_str) if time_str else '')
        my_datetime = datetime.strptime(date_time_str,
                                        ('%Y-%m-%d %H:%M:%S' if
                                         time_str else '%Y-%m-%d'))
        return my_datetime, interval  # , nap_id

    def compile_date_re(self):
        """
        :return: None
        Called by: main()
        """
        self.date_re = re.compile(r' \d{4}-\d{2}-\d{2} \|')


def main():
    chart = Chart('/home/jazcap53/python_projects/spreadsheet_etl/src/chart/chart_raw_data.txt')
    chart.compile_date_re()
    chart.read_file()


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
