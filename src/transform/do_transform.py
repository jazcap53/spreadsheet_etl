#!/usr/bin/python3.5


# file: src/transform/do_transform.py
# andrew jarcho
# 2017-03-12


def process_curr(cur_l):
    # print('in process_cur, cur_l is {}'.format(cur_l))
    out_val = None
    try:
        if cur_l == '':
            pass
        elif cur_l[0] == 'W':
            pass
        elif cur_l[0] == '=':
            pass
        elif cur_l[0] == ' ':
            out_val = cur_l
        elif cur_l[: 9] == 'action: b':
            out_val = cur_l
        elif cur_l[: 9] == 'action: s':
            out_val = cur_l
        elif cur_l[: 9] == 'action: w':
            out_val = cur_l
    except IndexError:
        print('BAD VALUE {} in input'.format(cur_l))
    else:
        if out_val is not None:
            print(out_val)


def read_each_line():  # from outp.stdout, which has been set to PIPE
    while True:
        try:
            curr_line = input()
        # while True:
        #     try:
        #         next_line = input()
        #         process_curr(curr_line, next_line)
            process_curr(curr_line)
        #         curr_line = next_line
        except EOFError:
            break
        # process_curr(curr_line)
    # except EOFError:
    #     pass


if __name__ == '__main__':
    read_each_line()
