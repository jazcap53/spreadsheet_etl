#!/usr/bin/python3


# file: src/transform/do_transform_closure.py
# andrew jarcho
# 2017-03-12


"""
Read lines from stdin, transform to a db-friendly format, and write to stdout.

The output will be usable by the database with a minimum of further
processing, and will hold all relevant data from the input.
"""

def process_curr():
    """
    Return a closure that will process a single line of input.

    Called by: read_each_line()
    Return: the closure, inner.

    """
    out_val = None
    last_date = ''
    last_sleep_time = ''

    def get_wake_or_last_sleep(cur_l):
        """
        Extract and return the time part of its string argument.

        Input time may be in 'h:mm' or 'hh:mm' format.
        Called by: inner().
        Return: Extracted time as a string in 'hh:mm' format.
        """
        end_pos = cur_l.rfind(', hours: ')
        out_time = cur_l[17: ] if end_pos == -1 else cur_l[17: end_pos]
        if len(out_time) == 4:
            out_time = '0' + out_time
        return out_time

    def get_duration(w_time, s_time):
        """
        Calculate the interval between w_time and s_time.

        Arguments are strings representing times in 'hh:mm' format.
        get_duration() calculates the interval between them as a
        string in decimal format e.g.,
            04.25 for 4 1/4 hours
        Called by: inner()
        Return: the calculated interval, whose value will be
                non-negative.
        """
        w_time_list = list(map(int, w_time.split(':')))
        s_time_list = list(map(int, s_time.split(':')))
        if w_time_list[1] < s_time_list[1]:  # wake minit < sleep minit
            w_time_list[1] += 60
            w_time_list[0] -= 1
        if w_time_list[0] < s_time_list[0]:  # wake hour < sleep hour
            w_time_list[0] += 24
        dur_list = [(w_time_list[x] - s_time_list[x]) for x in range(len(w_time_list))]
        duration = str(dur_list[0])
        if len(duration) == 1:  # change hour from '1' to '01', e.g.
            duration = '0' + duration
        if dur_list[1] == 15:
            duration += '.25'
        elif dur_list[1] == 30:
            duration += '.50'
        elif dur_list[1] == 45:
            duration += '.75'
        elif dur_list[1] == 0:
            duration += '.00'
        return duration

    def inner(cur_l):
        """
        A closure that processes a single line of input.

        Takes a string argument, and may output a single line to stdout.
        The output may depend on values from previous input strings,
        as well as on values in the current input string. Output is
        formatted as:
           'NIGHT, date, time'  or
           'NAP, time, duration'
        Returns: None
        """
        nonlocal out_val, last_date, last_sleep_time
        nonlocal get_wake_or_last_sleep, get_duration
        try:
            if cur_l == '':
                pass
            elif cur_l[0] == 'W':  # 'Week of ...'
                pass
            elif cur_l[0] == '=':  # '========...'
                pass
            elif cur_l[0] == ' ':  # a date in the format '    yyyy-mm-dd'
                last_date = cur_l[4: ]
            elif cur_l[: 9] == 'action: b':
                last_sleep_time = get_wake_or_last_sleep(cur_l)
                out_val = 'NIGHT, {}, {}'.format(last_date, last_sleep_time)
            elif cur_l[: 9] == 'action: s':
                last_sleep_time = get_wake_or_last_sleep(cur_l)
            elif cur_l[: 9] == 'action: w':
                wake_time = get_wake_or_last_sleep(cur_l)
                duration = get_duration(wake_time, last_sleep_time)
                # out_val = 'NAP, {}, {}'.format(wake_time, duration)  # TODO: should be .format(last_sleep_time, duration) ?
                out_val = 'NAP, {}, {}'.format(last_sleep_time, duration)
        except IndexError:
            print('BAD VALUE {} in input'.format(cur_l))
        else:
            if out_val is not None:
                print(out_val)
            out_val = None
    return inner

def read_each_line():
    """
    Read a line at a time from stdin; write to stdout.

    stdin is tied to stdout from the 'extract' phase subprocess.
    Called by: __main__()
    """
    line_processor = process_curr()
    while True:
        try:
            curr_line = input()
            line_processor(curr_line)
        except EOFError:
            break


if __name__ == '__main__':
    read_each_line()