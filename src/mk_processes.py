# file: src/mk_processes.py
# andrew jarcho
# 2017-02-24


"""
Create and connect the subprocesses that run the extract, transform,
and load stages.

logging_process runs the network logging receiver that allows all 3 stages
to log to the same file.
"""
import argparse
import subprocess
import time


def pop_cla_as_str(args_as_dict, arg_str):
    """Remove the arg_str argument from args_as_dict, if present"""
    ret = str(args_as_dict.pop(arg_str, False))
    return ret


note = 'Does not store to db unless -s switch is given.'
parser = argparse.ArgumentParser(description=note)
parser.add_argument('infile_name', help='The name of a .csv file to read')
parser.add_argument('-s', '--store', help='Store output in database',
                    action='store_true')
chart = parser.add_mutually_exclusive_group()

chart.add_argument('-c', '--chart', help='Output a sleep chart',
                   action='store_true')
chart.add_argument('-d', '--debug-chart', help='Output a sleep chart'
                   ' in debug mode', action='store_true')
args = parser.parse_args()

args_dict = args.__dict__
# these cla's will be converted to str(True) or str(False)
store_in_db = pop_cla_as_str(args_dict, 'store')
print_chart = pop_cla_as_str(args_dict, 'chart')
# debug-chart is converted to debug_chart by ArgumentParser()
print_debug_chart = pop_cla_as_str(args_dict, 'debug_chart')

logging_process = subprocess.Popen(
    ['./src/logging/receiver.py'],
)

time.sleep(1)

extract_process = subprocess.Popen(
    ['./src/extract/run_it.py', args.infile_name, store_in_db,
     print_chart, print_debug_chart],
    stdout=subprocess.PIPE,
)

time.sleep(2)

transform_process = subprocess.Popen(
    ['./src/transform/do_transform.py'],
    stdin=extract_process.stdout,
    stdout=subprocess.PIPE,
)

time.sleep(3)

load_process = subprocess.Popen(
    ['./src/load/load.py', store_in_db],
    stdin=transform_process.stdout,
)

time.sleep(7)

chart_input_filename = '/tmp/chart_input_bDX03c.txt'
if print_chart == 'True':
    chart_process = subprocess.Popen(
        ['./src/chart/chart_new.py',
         '-i', chart_input_filename],
    )
elif print_debug_chart == 'True':
    chart_process = subprocess.Popen(
        ['./src/chart/chart_new.py',
         '-i', chart_input_filename,
         '-d'],
    )
else:
    chart_process = None

time.sleep(2)

extract_process.terminate()
transform_process.terminate()
load_process.terminate()
if chart_process:
    chart_process.terminate()
logging_process.terminate()
