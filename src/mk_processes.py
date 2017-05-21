# file: src/mk_processes.py
# andrew jarcho
# 2017-02-24


"""
Create and connect the subprocesses that run the extract and transform stages.
"""

import subprocess
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('infile_name', help='The name of a .csv file to read')
# TODO: implement the below
# parser.add_argument('-s', '--store', help='Store output in database',
#                    action='store_true')
args = parser.parse_args()

extract_p = subprocess.Popen(
    ['./src/extract/run_it.py', args.infile_name],
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
