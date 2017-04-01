# file: src/mk_processes.py
# andrew jarcho
# 2017-02-24


"""
Create and connect the subprocesses that run the extract and transform stages.
"""

import subprocess
import time


extract_p = subprocess.Popen(
        ['./src/extract/run_it.py', './src/sheet_004.csv'],
        stdout=subprocess.PIPE,
)

transform_p = subprocess.Popen(
        ['./src/transform/do_transform_closure.py'],
        stdin=extract_p.stdout,
)

time.sleep(0.3)

extract_p.terminate()
transform_p.terminate()
