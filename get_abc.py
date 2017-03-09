#!/usr/bin/python3.5

# file: get_abc.py
# andrew jarcho
# 2017-03-08

# quick and dirty


from collections import defaultdict


triples = defaultdict(int)


def make_output_line(l_1, l_2 = None, l_3 = None):
    input_line = [l_1, l_2, l_3]
    output_line = []
    abc_line = ''
    global triples
    for item in input_line:
        if item == '':
            output_line.append('blank')
            abc_line += 'A'
        elif item is None:
            output_line.append('None ')
            abc_line += 'F'
        elif item[: 5] == 'Week ':
            output_line.append('Week ')
            abc_line += 'B'
        elif item[: 5] == '=====':
            output_line.append('=====')
            abc_line += 'C'
        elif item[: 5] == '    2':
            output_line.append('    2')
            abc_line += 'D'
        elif item[: 5] == 'actio':
            action_type = item[8]
            string_to_append = 'act=' + action_type
            output_line.append(string_to_append)
            abc_line += action_type
        else:
            output_line.append(item)  # TODO: raise exception here
            abc_line = 'BONGO'
    print('{} --- {}'.format(output_line, abc_line))
    triples[abc_line] += 1


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
    for k in sorted(triples.keys()):
        print('{}: {}'.format(k, triples[k]))
