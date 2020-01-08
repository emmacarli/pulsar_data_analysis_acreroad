# =============================================================================
# 
# This code plots a comparison of all raw and cleaned pulsar data files. 
# Author: Emma Carli 
#
# =============================================================================


#%% Clear variables

from IPython import get_ipython
get_ipython().magic('reset -f') 

#%% Import packages

import matplotlib.pyplot as plt
import numpy as np
import glob
from astropy.time import Time


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

#%% Set known variables

sampling_period = 2e-3 #2 ms
one_second_in_datapoints = int(1/sampling_period) #500 datapoints = 1 second of recording
one_minute_in_datapoints= one_second_in_datapoints * 60

#%% Go through each raw file
raw_files = glob.glob('/home/emma/Desktop/Raw_Datafiles/*-PSRB0329-2ms-sampling-dd.dat') #list of raw files on my computer

for file_raw in raw_files: #go through each raw file
    start_time_GPS = float(file_raw[33:-29])


    #%% If this file has already been plotted, skip it and go to the next in raw_files
    
    if glob.glob('Plots/'+str(start_time_GPS)+'_Compare_Cleaned_Raw*') != []:
        print(str(start_time_GPS)+' already plotted.')
        continue
    
    #%% Access the raw data
    handle_file_raw = open(file_raw, mode='rb') 
    data_raw = np.fromfile(handle_file_raw,'f4')
    
    
    #%% Access the cleaned data and handle exceptions
    try:
        file_cleaned = '/home/emma/Desktop/Cleaned_Data/'+str(start_time_GPS)+'_cleaned.dat'
        handle_file_cleaned = open(file_cleaned)
        data_cleaned = np.fromfile(handle_file_cleaned,'f4')
    except FileNotFoundError:
        print(str(start_time_GPS)+' has no cleaned file and has been skipped.')
        continue

    #%% Plot a comparison of the raw file and its cleaned version
    


    #%% Calculate values for axes and ticks
    
    flag = ''
    
    #Raw dataset
    total_seconds_raw = len(data_raw)*sampling_period
    total_hours_raw =  total_seconds_raw / 3600
    total_hours_rounded_raw = np.ceil(total_hours_raw)
    total_hours_rounded_datapoints_raw =total_hours_rounded_raw*3600/sampling_period
     
    if total_hours_rounded_raw not in [4.0, 5.0]:
        flag = '_different_length'
     
    #Cleaned dataset
    total_seconds_cleaned = len(data_cleaned)*sampling_period #total seconds in dataset
    total_hours_cleaned =  total_seconds_cleaned / 3600 #total hours in dataset
    total_hours_rounded_cleaned = np.ceil(total_hours_cleaned) #total rounded hours in dataset
    total_hours_rounded_datapoints_cleaned = total_hours_rounded_cleaned*3600/sampling_period #how many datapoints in total rounded hours in dataset
        

    #%% Set axes and ticks
    
    #Cleaned dataset
    major_ticks_cleaned = np.linspace(0, total_hours_rounded_datapoints_cleaned, num=total_hours_rounded_cleaned+1) #set big ticks every hour
    minor_ticks_cleaned = np.linspace(0, total_hours_rounded_datapoints_cleaned, num=((total_hours_rounded_cleaned*60)+1)) #set small ticks every minute
    
    #Raw dataset
    major_ticks_raw = np.linspace(0, total_hours_rounded_datapoints_raw, num=total_hours_rounded_raw+1) #set big ticks every hour
    minor_ticks_raw = np.linspace(0, total_hours_rounded_datapoints_raw, num=((total_hours_rounded_raw*60)+1)) #set small ticks every minute
    
    #%% Plot raw and cleaned files
    
    fig1 = plt.figure()
    
    #Cleaned dataset
    fig1_top = fig1.add_subplot(2,1,1)
    fig1_top.plot(data_cleaned, color='black',  marker='None', linewidth=0.05) 
    fig1_top.set_ylabel('Power (arbitrary units)')
    fig1_top.set_xticks(major_ticks_cleaned)
    fig1_top.set_xticks(minor_ticks_cleaned, minor=True)
    fig1_top.grid(which='minor', alpha=0.2)
    fig1_top.grid(which='major', alpha=0.5)
    fig1_top.set_xticklabels(np.linspace(0, total_hours_rounded_cleaned, num=total_hours_rounded_cleaned+1))
    fig1_top.set_title('Cleaned Data')
    
    #Raw dataset
    fig1_bottom = fig1.add_subplot(2,1,2)
    fig1_bottom.plot(data_raw, color='black', marker='None', linewidth=0.05) 
    fig1_bottom.set_xlabel('Time since start (hours)')
    fig1_bottom.set_ylabel('Power (arbitrary units)')
    fig1_bottom.set_xticks(major_ticks_raw)
    fig1_bottom.set_xticks(minor_ticks_raw, minor=True)
    fig1_bottom.grid(which='minor', alpha=0.2)
    fig1_bottom.grid(which='major', alpha=0.5)
    fig1_bottom.set_xticklabels(np.linspace(0, total_hours_rounded_raw, num=total_hours_rounded_raw+1))
    fig1_bottom.set_title('Raw data')
               
        
# =============================================================================
#     HERE THE TIME FORMAT HAS BEEN SET BUT NOT THE SCALE/TIME STANDARD. THIS IS NOT PRECISE -- BUT ONLY FOR A PLOT SO THAT'S OK.
# =============================================================================
        
    #now convert the GPS time string  into astropy time format
    start_time_GPS_astropy = Time(start_time_GPS, format='gps') 
    start_time_ISO_astropy = Time(start_time_GPS_astropy, format='iso')
    
    
    fig1.suptitle('Start of recording: ' + start_time_ISO_astropy.value)
    plt.subplots_adjust(hspace=0.5)
    
    
    plt.savefig('Plots/'+str(start_time_GPS)+'_Compare_Cleaned_Raw'+flag+'.pdf') 
    plt.close()
