#!/usr/bin/python3.5


# file: src/transform/do_transform.py
# andrew jarcho
# 2017-03-12


def process_curr():
    # print('in process_cur, cur_l is {}'.format(cur_l))
    out_val = None
    last_date = ''
    last_sleep_time = ''
    multiplier = 0
    def inner_process_curr(cur_l):
        nonlocal out_val, last_date, last_sleep_time, multiplier
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
                # next 5 lines: needed because 'time: ' part of cur_l may
                # be 'h:mm' or 'hh:mm'
                end_pos = cur_l.rfind(', hours: ')
                if end_pos != -1:
                    last_sleep_time = cur_l[17: end_pos]
                else:
                    last_sleep_time = cur_l[17: ]
                out_val = 'NIGHT, {}, {}'.format(last_date, last_sleep_time)
            elif cur_l[: 9] == 'action: s':
                # last_sleep_time = cur_l[17: ]
                # next 5 lines: needed because 'time: ' part of cur_l may
                # be 'h:mm' or 'hh:mm'
                end_pos = cur_l.rfind(', hours: ')
                if end_pos != -1:
                    last_sleep_time = cur_l[17: end_pos]
                else:
                    last_sleep_time = cur_l[17: ]
            elif cur_l[: 9] == 'action: w':
                w_action_time = cur_l[17: ]
                if w_action_time < last_sleep_time:
                    multiplier = 1
                else:
                    multiplier = 0
                # TODO: stuff goes here to calculate interval output
                out_val = 'NAP, something, something<, something>'
        except IndexError:
            print('BAD VALUE {} in input'.format(cur_l))
        else:
            if out_val is not None:
                print(out_val)
            out_val = None
    return inner_process_curr


def read_each_line():  # from outp.stdout, which has been set to PIPE
    line_processor = process_curr()
    while True:
        try:
            curr_line = input()
        # while True:
        #     try:
        #         next_line = input()
        #         process_curr(curr_line, next_line)
            line_processor(curr_line)
        #         curr_line = next_line
        except EOFError:
            break
        # process_curr(curr_line)
    # except EOFError:
    #     pass


if __name__ == '__main__':
    read_each_line()
