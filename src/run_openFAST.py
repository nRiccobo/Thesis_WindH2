'''
This script runs a baseline openFAST simulation of the IEA-3.4MW Wind turbine
'''
# Load Python Modules
import os

# Load my modules
import utilities as util

# ROSCO Modules
from ROSCO_toolbox import controller as ROSCO_controller
from ROSCO_toolbox import turbine as ROSCO_turbine
from ROSCO_toolbox.utilities import run_openfast
from ROSCO_toolbox.inputs.validation import load_rosco_yaml
from datetime import datetime

# WHAT? User inputs
input_file = 'IEA3p4MW.yaml' #'NREL3p4MW.yaml' # IEA15MW.yaml
wind_speed = 10.0
rated_power = 3400000

runFast = True # Set False for debugging all file movement
save = False
project_name = input_file.split('.')[0] + datetime.today().strftime('%Y%m%d')

## WHERE? Directories and stuff
this_dir = os.getcwd()
root_dir = os.path.join(this_dir, os.pardir)

# specify the input directory for each turbine's config file
input_dir = os.path.join(root_dir, 'inputs')

# specify the output directory 
output_dir = os.path.join(root_dir,'results', project_name)
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

# paths to WEIS's binary files
weis_dir = os.path.join(root_dir, os.pardir, 'WEIS') # System append? or imports?
ofbin_dir=os.path.join(weis_dir, 'local', 'bin', 'openfast')

## WHO? Gather turbine parameters from input file
inps = load_rosco_yaml(os.path.join(input_dir, input_file))
path_params         = inps['path_params']
turbine_params      = inps['turbine_params']
controller_params   = inps['controller_params']

# initiate turbine with ROSCO toolboxes 
turbine         = ROSCO_turbine.Turbine(turbine_params)
controller      = ROSCO_controller.Controller(controller_params)
rotorperf_file = path_params['rotor_performance_filename']

## HOW? Specify OpenFast files
fast_dir = os.path.join(root_dir, path_params['FAST_directory']) 
fast_file = path_params['FAST_InputFile']

# set new inflow speed by rewriting line in Inflow file
util.set_new_inflow_speed(fast_dir, wind_speed, verbose=True) 

# set rated power or other params in other files

# Load turbine data from OpenFAST and rotor performance text files
turbine.load_from_fast(fast_file, fast_dir, \
    dev_branch=True,rot_source='txt',\
      txt_filename=os.path.join(this_dir,fast_dir,rotorperf_file))

# WHEN? Run OpenFAST now!
if runFast:
    run_openfast(fast_dir,fastcall=ofbin_dir,fastfile=fast_file,chdir=True)
    print("Completed Run: {} m/s with {} rated power".format(wind_speed, rated_power))

# WHY? Save the results of the sim and move to output directory
util.save_fast_files(fast_dir, output_dir, saveOn=save, verbose=True)

