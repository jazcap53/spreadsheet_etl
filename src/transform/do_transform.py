#!/usr/bin/python3.5


# file: src/transform/do_transform.py
# andrew jarcho
# 2017-03-12


def process_curr():
    """
    Called by: read_each_line()
    Returns: inner_process_curr()
    """
    out_val = None
    last_date = ''
    last_sleep_time = ''
    multiplier = 0


    def get_wake_or_last_sleep(cur_l):
        """
        Called by: inner_process_curr().
        Returns: the 'time' part of cur_l which may be in 'h:mm' or
                 'hh:mm' format.
        """
        end_pos = cur_l.rfind(', hours: ')
        out_time = cur_l[17: ] if end_pos == -1 else cur_l[17: end_pos]
        if len(out_time) == 4:
            out_time = '0' + out_time
        return out_time


    def get_duration(w_time, s_time):
        """
        Called by: inner_process_curr()
        Returns: the difference between the wake and sleep times,
                 expressed as a string in decimal format, e.g.,
                 04.25 for 4 1/4 hours.
        """
        w_time_list = list(map(int, w_time.split(':')))  # w: wake
        s_time_list = list(map(int, s_time.split(':')))  # s: sleep
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


    def inner_process_curr(cur_l):
        """
        Called by: inner_process()
        Returns: None
        Prints argument to stdout as a string in format:
               NIGHT, date, time  or
               NAP, time, duration
        """
        nonlocal out_val, last_date, last_sleep_time, multiplier
        nonlocal get_wake_or_last_sleep, get_duration
        try:
            if cur_l == '':
                pass
            elif cur_l[0] == 'W':
                pass
            elif cur_l[0] == '=':
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
                out_val = 'NAP, {}, {}'.format(wake_time, duration)
        except IndexError:
            print('BAD VALUE {} in input'.format(cur_l))
        else:
            if out_val is not None:
                print(out_val)
            out_val = None

    return inner_process_curr


def read_each_line():  # from outp.stdout, which has been set to PIPE
    """
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
