#!/usr/bin/python3.5


# file: src/transform/get_input.py
# andrew jarcho
# 2017-02-22


def process_curr(cur_l, nxt_l = None):
    out_val = None
    if cur_l[:5] == '    2' and nxt_l is not None and nxt_l[:5] == 'actio':
        out_val = cur_l
    elif cur_l[:5] == 'actio':
        out_val = cur_l
    if out_val is not None:
        print(out_val)


def read_each_line():
    try:
        curr_line = input()
        while True:
            try:
                next_line = input()
                process_curr(curr_line, next_line)
                curr_line = next_line
            except EOFError:
                break
        process_curr(curr_line)
    except EOFError:
        pass


if __name__ == '__main__':
    read_each_line()
