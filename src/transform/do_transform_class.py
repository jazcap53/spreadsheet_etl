#!/usr/bin/python3.5


# file: src/transform/do_transform_class.py
# andrew jarcho
# 2017-03-16


"""
Read lines from stdin, transform to a db-friendly format, and write to stdout.

process_curr() takes a string as an argument, and prints a corresponding
command to stdout that may be used to load data from the argument string
into the db.
"""

class Transform(object):

    def __init__(self):
        self.out_val = None
        self.last_date = ''
        self.last_sleep_time = ''
        self.multiplier = 0

    def read_each_line(self):
        """
        Called by: __main__()
        Read from the 'extract' phase output; write to stdout.
        """
        while True:
            try:
                curr_line = input()
                self.process_curr(curr_line)
            except EOFError:
                break

    def process_curr(self, cur_l):
        """
        Called by: read_each_line()
        Returns: None
        Prints argument to stdout as a string in format:
               'NIGHT, date, time'  or
               'NAP, time, duration'
        """
        try:
            if cur_l == '':
                pass
            elif cur_l[0] == 'W':  # 'Week of ...'
                pass
            elif cur_l[0] == '=':  # '========...'
                pass
            elif cur_l[0] == ' ':  # a date in the format '    yyyy-mm-dd'
                self.last_date = cur_l[4: ]
            elif cur_l[: 9] == 'action: b':
                self.last_sleep_time = self.get_wake_or_last_sleep(cur_l)
                self.out_val = 'NIGHT, {}, {}'.format(self.last_date, self.last_sleep_time)
            elif cur_l[: 9] == 'action: s':
                self.last_sleep_time = self.get_wake_or_last_sleep(cur_l)
            elif cur_l[: 9] == 'action: w':
                wake_time = self.get_wake_or_last_sleep(cur_l)
                duration = self.get_duration(wake_time, self.last_sleep_time)
                self.out_val = 'NAP, {}, {}'.format(wake_time, duration)
        except IndexError:
            print('BAD VALUE {} in input'.format(cur_l))
        else:
            if self.out_val is not None:
                print(self.out_val)
            self.out_val = None

    def get_wake_or_last_sleep(self, cur_l):
        """
        Called by: process_curr().
        Returns: the 'time' part of cur_l, which it receives in 'h:mm' or
                 'hh:mm' format.
        """
        end_pos = cur_l.rfind(', hours: ')
        out_time = cur_l[17: ] if end_pos == -1 else cur_l[17: end_pos]
        if len(out_time) == 4:
            out_time = '0' + out_time
        return out_time

    def get_duration(self, w_time, s_time):
        """
        Called by: process_curr()
        Returns: the difference between the wake and sleep times,
                 expressed as a string in decimal format, e.g.,
                 04.25 for 4 1/4 hours.
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


if __name__ == '__main__':
    t = Transform()
    t.read_each_line()
