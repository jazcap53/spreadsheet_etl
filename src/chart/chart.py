class Chart:
    to_unicode = {0: '\u0020', 1: '\u2590', 2: '\u258c',
                  3: '\u2588', 7: '\u2591'}

    def __init__(self):
        pass

    @staticmethod
    def get_half_hr(code):
        return Chart.to_unicode[code]

    @staticmethod
    def make_out_string(line_in):
        temp = [Chart.get_half_hr(int(i)) for i in line_in.decode()]
        line_out = ''.join(temp)
        return line_out


Chart.make_out_string(bytearray
                      ('771333200013332000133320001333200013332000133320',
                       'utf-8'))
