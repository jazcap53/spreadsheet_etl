#!/usr/bin/python3.5

# file: get_abc.py
# andrew jarcho
# 2017-03-08

# quick and dirty



def make_output_line(l_1, l_2 = None, l_3 = None):
    input_line = [l_1, l_2, l_3]
    output_line = []
    for item in input_line:
        if item == '':
            output_line.append('blank')
        elif item is None:
            output_line.append('None ')
        elif item[:5] in ['Week ', '=====', '    2', 'actio']:
            output_line.append(item[:5])
        else:
            output_line.append(item)  # TODO: raise exception here
    print(output_line)


def read_input():
    try:
        line_1 = input()
        try:
            line_2 = input()
            while True:
                try:
                    line_3 = input()
                    make_output_line(line_1, line_2, line_3)
                    line_1 = line_2
                    line_2 = line_3
                except EOFError:
                    make_output_line(line_1, line_2)
                    break
        except EOFError:
            make_output_line(line_1)
    except EOFError:
        pass


if __name__ == '__main__':
    read_input()
