class Chart:
    to_glyph = {0: '\u0020', 1: '\u2590', 2: '\u258c',
                  3: '\u2588', 7: '\u2591'}

    def __init__(self):
        pass

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
