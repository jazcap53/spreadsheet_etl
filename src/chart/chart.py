# file: chart.py
# andrew jarcho
# 10/2018


from tests.file_access_wrappers import FileReadAccessWrapper


class Chart:
    """
    Create a sleep chart from input data
    """
    to_glyph = {0: '\u2588', 1: '\u258c', 2: '\u2590',
                3: '\u0020', 7: '\u2591'}

    ASLEEP = 0b0  # the printed color (black ink)
    AWAKE = 0b1  # the background color (white paper)

    def __init__(self, infile):
        self.infile = infile
        self.cur_line = ''

    def get_a_line(self):
        pass  # TODO: NYI

    @staticmethod
    def quarter_to_digit(q):
        """
        Return one bit per quarter hour
        :param q: the state(asleep or awake) during a quarter hour
        :return: 0-bit for asleep, 1-bit for awake
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
        """
        return hi_bit << 1 | lo_bit

    @staticmethod
    def make_glyph(code):
        """
        A glyph names a Unicode Block Element code point
        :param code: a 2-bit code representing a glyph in dict to_glyph
        :return: the glyph associated with the 2-bit code
        """
        return Chart.to_glyph[code]

    @staticmethod
    def make_out_string(line_in):
        """
        Convert bytearray with 2-bit values 0,1,2,3,or 7 to a string of glyphs
        :param line_in:
        :return:
        """
        assert len(line_in)
        return ''.join([Chart.make_glyph(int(i)) for i in line_in.decode()])


if __name__ == '__main__':
    print(Chart.make_out_string
          (bytearray
           ('771333200013332000133320001333200013332000133320',
            'utf-8')))
    print(Chart.make_out_string
          (bytearray
           ('000000000000000000000000000000000000000000000000',
            'utf-8')))
    chart = Chart(FileReadAccessWrapper('chart_raw_data.txt'))
