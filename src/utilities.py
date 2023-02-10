''' Utility file comprised of functions to parse and manage openFast simulations

===================
find_datfiles = get a list of all accompanying .dat files for a turbine 

'''
import os
import shutil
import re

def find_datfiles(sim_dir, verbose=False):

    dat_keys = ['AeroDyn15', 'AeroDyn15_blade', 'ElastoDyn_blade', 
        'ElastoDyn_tower', 'ElastoDyn', 'InflowFile', 'ServoDyn']
    dat_dict = {}

    if verbose: 
        print("Looking in {} for .dat files".format(os.path.abspath(sim_dir)))

    dat_vals = list_of_files(sim_dir, '.dat')
    
    for k in dat_keys:
        
        match = {k: v for v in dat_vals if (k + '.') in v}
        dat_dict.update(match)
    
    if verbose: print(dat_dict)

    return dat_dict

def make_temp_files(sim_dir):

    # make a temporary directory  
    temp_dir = os.path.join(sim_dir, 'temp')
    if not os.path.isdir(temp_dir):
        os.makedirs(temp_dir)

    # find the .fst file and copy it to temp
    fst_file = list_of_files(sim_dir, '.fst')
    
    for ff in fst_file:
        shutil.copy(os.path.join(sim_dir, ff), temp_dir)

    # find the .dat files and copy them to temp
    dat_dict = find_datfiles(sim_dir)

    dat_list = dat_dict.values()
    
    for fd in dat_list:
        shutil.copy(os.path.join(sim_dir,fd), temp_dir)
    
    return temp_dir

def set_new_inflow_speed(datfiles_dir, new_speed, verbose=True):
    
    dat_dict = find_datfiles(datfiles_dir)
    inflow_file = dat_dict['InflowFile']

    var_name = 'HWindSpeed'

    with open(os.path.join(datfiles_dir, inflow_file),'r') as f:

        contents = ''
        lines = f.readlines()

        for row in lines:
            
            if row.find(var_name) != -1:
                #print("var found line: ", lines.index(row))
                if row.split(' ')[0] != str(new_speed): 
                    if verbose: print("New windspeed:  ", new_speed, "m/s")
                    row = re.sub(row.split(' ')[0], str(new_speed), row)

            contents = contents + row 

    f.close()
    
    with open(os.path.join(datfiles_dir, inflow_file), 'w') as fw:

        fw.write(contents)

    fw.close

def save_fast_files(sim_dir, dest_dir, saveOn=True, verbose=False):

    file_type = '.outb'
    # Get the list of out files from the sim directory
    out_files = list_of_files(sim_dir, file_type)
    
    # Check if the destination directory exists
    if not os.path.isdir(dest_dir):
        os.makedirs(dest_dir)
    
    # Check if there are files already in the destination directory
    dest_files = list_of_files(dest_dir, file_type)
    
    # Find the last file saved. Looking for 000.out suffix
    max_id = 0 
    for d in dest_files: 

        try:
            file_id = d.split('.')[0][-3:]
            
            if int(file_id) > max_id: max_id = int(file_id) 

        except ValueError:
            pass

    count = max_id

    if saveOn: 
       
        count+=1
        new_file_id = '_' + ("%03d" % count)
        new_file = out_files[0].split('.')[0] + new_file_id + file_type

        shutil.copy(os.path.join(sim_dir,out_files[0]), 
                os.path.join(dest_dir, new_file))

        if verbose: print("Saving file: ", new_file)
    
    else: 
        if verbose: print("No file saved...")

def list_of_files(files_dir, file_ext):

    list_files = [f for f in os.listdir(files_dir)
        if f.endswith(file_ext) and os.path.isfile(os.path.join(files_dir, f))]

    return list_files


