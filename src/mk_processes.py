# file: src/mk_processes.py
# andrew jarcho
# 2017-02-24


"""
Build and link the subprocesses that run the extract and transform stages.
"""

import subprocess
import time


outp = subprocess.Popen(
        ['./src/extract/run_it.py', './src/sheet_004.csv'],
        stdout=subprocess.PIPE,
)

inp = subprocess.Popen(
        ['./src/transform/do_transform.py'],
        stdin=outp.stdout,
)

time.sleep(0.1)

outp.terminate()
inp.terminate()
