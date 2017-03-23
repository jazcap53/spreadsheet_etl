# file: src/mk_processes.py
# andrew jarcho
# 2017-02-24


"""
Create and connect the subprocesses that run the extract and transform stages.
"""

import subprocess
import time


outp = subprocess.Popen(
        ['./src/extract/tmp_run_it.py', './src/sheet_004.csv'],
        stdout=subprocess.PIPE,
)

inp = subprocess.Popen(
        ['./src/transform/do_transform_closure.py'],
        stdin=outp.stdout,
)

time.sleep(0.3)

outp.terminate()
inp.terminate()
