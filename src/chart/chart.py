# file: chart.py
# andrew jarcho
# 10/2018


from tests.file_access_wrappers import FileReadAccessWrapper
import re
import sys


class Chart:
    """
    Create a sleep chart from input data
    """
    to_glyph = {0: '\u2588',  # FULL BLOCK xx█xx
                1: '\u258c',  # LEFT HALF BLOCK xx▌xx
                2: '\u2590',  # RIGHT HALF BLOCK xx▐xx
                3: '\u0020',  # SPACE xx xx
                7: '\u2591'}  # LIGHT SHADE xx░xx

    ASLEEP = 0b0  # the printed color (black ink)
    AWAKE = 0b1  # the background color (white paper)

    def __init__(self, filename):
        self.filename = filename
        self.infile = None
        self.cur_line = ''
        self.prev_line = ''
        self.sleep_state = self.AWAKE
        self.date_re = None

    def get_a_line(self):
        """

        :return:
        Called by: open_file()
        """
        self.cur_line = self.infile.readline().rstrip()
        while self.cur_line and not self.date_re.match(self.cur_line):
            self.cur_line = self.infile.readline().rstrip()
        return bool(self.cur_line)

    @staticmethod
    def quarter_to_digit(q):
        """
        Return one bit per quarter hour
        :param q: the state(asleep or awake) during a quarter hour
        :return: 0-bit for asleep, 1-bit for awake
        Called by:
        """
        if q:
            return Chart.AWAKE
        return Chart.ASLEEP

    @staticmethod
    def quarters_to_glyph_code(hi_bit, lo_bit):
        """
        Convert 2 1-bit quarters to a 2-bit code
        :param hi_bit: high order bit
        :param lo_bit: low order bit
        :return: a 2-bit code representing a quarter hour
        Called by:
        """
        return hi_bit << 1 | lo_bit

    @staticmethod
    def make_glyph(code):
        """
        A glyph names a Unicode Block Element code point
        :param code: a 2-bit code representing a glyph in dict to_glyph
        :return: the glyph associated with the 2-bit code
        Called by: make_out_string()
        """
        return Chart.to_glyph[code]

    @staticmethod
    def make_out_string(line_in):
        """
        Convert bytearray with 2-bit values 0,1,2,3,or 7 to a string of glyphs
        :param line_in:
        :return:
        Called by: main()
        """
        assert len(line_in)
        return ''.join([Chart.make_glyph(int(i)) for i in line_in.decode()])

    def open_file(self):
        """

        :return:
        Called by: main()
        """
        with open(self.filename) as self.infile:
            while self.get_a_line():
                print(self.cur_line)

    def compile_date_re(self):
        """

        :return:
        Called by: main()
        """
        self.date_re = re.compile(r' \d{4}-\d{2}-\d{2} \|')


def main():
    chart = Chart('/home/jazcap53/python_projects/spreadsheet_etl/src/chart/chart_raw_data.txt')
    chart.compile_date_re()
    chart.open_file()
    print(Chart.make_out_string
          (bytearray
           ('771333200013332000133320001333200013332000133320',
            'utf-8')))
    print(Chart.make_out_string
          (bytearray
           ('000000000000000000000000000000000000000000000000',
            'utf-8')))


if __name__ == '__main__':
    # chart = Chart(FileReadAccessWrapper('chart_raw_data.txt'))
    # chart = Chart('/home/jazcap53/python_projects/spreadsheet_etl/src/chart/chart_raw_data.txt')
    # chart.open_file()
    main()
