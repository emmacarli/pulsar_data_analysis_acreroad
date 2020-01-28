# =============================================================================
# 
# This code folds all the observations using PRESTO.
# Author: Emma Carli
#
# =============================================================================


#%% Clear variables

from IPython import get_ipython
get_ipython().magic('reset -f') 

#%% Import packages

import matplotlib.pyplot as plt
from astropy.time import Time
import glob
import numpy as np
import sys
import subprocess
from My_Functions.update_text import update_text
from shutil import copyfile
import os


#%% Set matplotlib general parameters

#Make everything larger for readability on graphs
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['font.size'] = 14
#Set same fonts as my LaTeX document
plt.rcParams['font.family'] = 'STIXGeneral' 
plt.rcParams['mathtext.fontset'] = 'stix'
#other plotting params
plt.rcParams['axes.grid'] = True
plt.rcParams["figure.figsize"] = [10,10]

#%% Start a log
log_handle = open('PRESTO_Fold_All_Observations.log', 'w')

sys.stdout = log_handle
#sys.stderr = log_handle

#%% Set known variables

sampling_period = 2e-3 #2 ms
one_second_in_datapoints = int(1/sampling_period) #500 datapoints = 1 second of recording
one_minute_in_datapoints= one_second_in_datapoints * 60

#%% Find out time span of the available observations

cleaned_files = sorted(glob.glob('/home/emma/Desktop/Cleaned_Data/*_cleaned.dat'))
minimum_GPS_time = Time(float(cleaned_files[0][32:-12]), format='gps') #this is the first date at which I start having observations, extracted from the file name of the ordered cleaned files.
print('The observations start on ' + minimum_GPS_time.iso)
maximum_GPS_time = Time(float(cleaned_files[len(cleaned_files)-1][32:-12]), format='gps') #this is the last observation date
print('The observations end on ' + maximum_GPS_time.iso)
observations_span = maximum_GPS_time - minimum_GPS_time
print('The observations span '+str(observations_span.jd)+' days.')
print('\n \n \n \n') 

    #If try to generate TEMPO polycos for the whole observations span (in my case, a year), Nspan too small error even for hundreds of hours:
    #'tempo  -ZOBS=AR -ZFREQ=407.5 -ZTOBS='+str(np.ceil(observations_span.jd*24))+' -ZSTART='+str(np.floor(minimum_GPS_time.mjd))+'  -ZNCOEFF=15 -ZSPAN=1000H -f B0329+54.par'


#%%Loop through observations

for file_cleaned in cleaned_files:


    
    #%% Find out the start time and length of the observation
    
    
    start_time_GPS = float(file_cleaned[32:-12])
    start_time_GPS_astropy = Time(start_time_GPS, format='gps') 
    print('Observation starting on GPS time '+str(start_time_GPS)+' i.e. '+str(start_time_GPS_astropy.iso)+'\n')
    handle_file_cleaned = open(file_cleaned)
    data_cleaned = np.fromfile(handle_file_cleaned,'f4')
    #Cleaned dataset
    total_seconds_cleaned = len(data_cleaned)*sampling_period #total seconds in dataset
    total_hours_cleaned =  total_seconds_cleaned / 3600 #total hours in dataset
    total_hours_rounded_cleaned = np.ceil(total_hours_cleaned) #total rounded hours in dataset


    #%% Generate the TEMPO polycos for this observation
    
    #Create the custom TEMPO command for this file
    TEMPO_command = 'tempo -ZOBS=AR -ZFREQ=407.5 -ZTOBS='+str(total_hours_rounded_cleaned)+' -ZSTART='+str(start_time_GPS_astropy.mjd)+'  -ZNCOEFF=15 -ZSPAN='+str(int(total_hours_rounded_cleaned))+'H -f B0329+54.par'
    print('TEMPO command: ' + TEMPO_command)
    #I round the start time to start a tiny bit earlier

    terminal_TEMPO_run = subprocess.run(TEMPO_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    print(terminal_TEMPO_run.stdout.decode('utf-8'))
    
    
    #Here I add the name of the pulsar because for some reason, TEMPO does not put it in, and it is needed in PRESTO
    polyco_handle = open('polyco.dat','r+')
    polyco_contents = polyco_handle.read()
    polyco_handle.seek(0,0)
    polyco_handle.write('0332+5434  ')
    polyco_handle.close()
    
    
    #%% Create PRESTO .inf file
    #This file contains information about the observation essential to the PRESTO folding software
    #Modify a template inf file. It has empty slots that need filled.
    
    copyfile('Template_PRESTO_inf_file.txt','current_PRESTO_inf_file.inf') #this creates an empty template file, and removes the previous instance of it
    
    #Write the datafile name, without suffix
    update_text(filename='current_PRESTO_inf_file.inf', lineno=1, column=44, text=file_cleaned[:-4])
    
    #Write the observation start MJD
    update_text(filename='current_PRESTO_inf_file.inf', lineno=8, column=44, text=str(start_time_GPS_astropy.mjd))
    
    #Write the number of bins in the time series
    update_text(filename='current_PRESTO_inf_file.inf', lineno=10, column=44, text=str(len(data_cleaned)))
    
    #PRESTO will look for this information file in the same location as the data file, with the same name
    copyfile('current_PRESTO_inf_file.inf', file_cleaned[:-3]+'inf')

    
    #%% Perform the fold for this observation
    
    PRESTO_command = 'prepfold -nosearch -absphase -polycos polyco.dat -psr 0332+5434 -double -noxwin -o ~/Desktop/pulsardataprep_acreroad/Folding/PRESTO_Folded_Profiles/'+str(start_time_GPS)+' '+file_cleaned
    
    #to try: window
    
    print('PRESTO command: ' + PRESTO_command)
    
    
    terminal_PRESTO_run = subprocess.run(PRESTO_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    print(terminal_PRESTO_run.stdout.decode('utf-8'))

    
    
    
    print('\n \n \n \n')
    
    
    
    
    
    
    
    
    
#%% Clean up

log_handle.close()
os.remove('current_PRESTO_inf_file.inf')
os.remove('polyco.dat')

    
    
    
    
    
    
    
    
    
    
    
    

    
    



