#!/usr/bin/python3.5


# file: src/transform/get_input.py
# andrew jarcho
# 2017-02-22


while True:
    try:
        line = input().rstrip()
        print(line)
    except EOFError:
        break
