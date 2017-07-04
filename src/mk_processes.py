# file: src/mk_processes.py
# andrew jarcho
# 2017-02-24


# TODO: create more detailed docstring here
"""
Create and connect the subprocesses that run the extract and transform stages.
"""

import subprocess
import time
import argparse

note = 'Runs in debug mode unless -s switch is given.'
parser = argparse.ArgumentParser(description=note)
parser.add_argument('infile_name', help='The name of a .csv file to read')
parser.add_argument('-s', '--store', help='Store output in database',
                    action='store_true')
args = parser.parse_args()

# remove the --store argument from the args Namespace, if present
d = args.__dict__
store_in_db = str(d.pop('store', False))  # d[store] is set to True if present

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
    ['./src/load/load.py', store_in_db],
    stdin=transform_p.stdout,
)

time.sleep(3)

extract_p.terminate()
transform_p.terminate()
load_p.terminate()
