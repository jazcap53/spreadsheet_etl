class Chart:
    to_glyph = {0: '\u2588', 1: '\u258c', 2: '\u2590',
                3: '\u0020', 7: '\u2591'}

    ASLEEP = 0b0
    AWAKE = 0b1

    def __init__(self, outfile_name='outfile_test_name.txt'):
        self.outfile_name = outfile_name

    @staticmethod
    def quarter_to_digit(q):
        if q:
            return Chart.AWAKE
        return Chart.ASLEEP

    @staticmethod
    def quarters_to_glyph_code(hi_bit, lo_bit):
        return hi_bit << 1 | lo_bit

    @staticmethod
    def make_glyph(code):
        return Chart.to_glyph[code]

    @staticmethod
    def make_out_string(line_in):
        assert len(line_in)
        temp = [Chart.make_glyph(int(i)) for i in line_in.decode()]
        line_out = ''.join(temp)
        return line_out


if __name__ == '__main__':
    print(Chart.make_out_string
          (bytearray
           ('771333200013332000133320001333200013332000133320',
            'utf-8')))
