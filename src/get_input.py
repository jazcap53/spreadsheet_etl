#!/usr/bin/python3.5


# file: get_input.py
# andrew jarcho
# 2017-02-22


line = input().rstrip()
while True:
    print(line)
    try:
        line = input().rstrip()
    except EOFError:
        break
