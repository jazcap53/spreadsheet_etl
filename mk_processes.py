# file: mk_processes.py
# andrew jarcho
# 2017-02-24


import subprocess
import time


outp = subprocess.Popen(
        ['./src/run_it.py', './sheet_004.csv'],
        stdout=subprocess.PIPE,
)


inp = subprocess.Popen(
        ['./src/get_input.py'],
        stdin=outp.stdout,
)

time.sleep(0.1)

outp.terminate()
inp.terminate()
