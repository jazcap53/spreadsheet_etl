class Chart:
    to_unicode = {-1: '\u2591', 0: '\u0020', 1: '\u2590', 2: '\u258c',
                  3: '\u2588'}

    def __init__(self):
        pass
    
    @staticmethod
    def get_half_hr(code):
        return Chart.to_unicode[code]

