# file: src/mk_processes.py
# andrew jarcho
# 2017-02-24


"""
Create and connect the subprocesses that run the extract and transform stages.
"""

import sys
import subprocess
import time


if len(sys.argv) != 2:  # TODO: import argparse
    print('Usage: {} <input_file_name>'.format(sys.argv[0]))
    sys.exit(0)


extract_p = subprocess.Popen(
    ['./src/extract/run_it.py', sys.argv[1]],
    stdout=subprocess.PIPE,
)

transform_p = subprocess.Popen(
    ['./src/transform/do_transform_closure.py'],
    stdin=extract_p.stdout,
    stdout=subprocess.PIPE,
)

load_p = subprocess.Popen(
    ['./src/load/load.py'],
    stdin=transform_p.stdout,
)

time.sleep(1)

extract_p.terminate()
transform_p.terminate()
load_p.terminate()
