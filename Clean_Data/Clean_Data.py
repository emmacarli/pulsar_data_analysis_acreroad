# =============================================================================
# 
# This code cleans all raw pulsar data files. 
# Author: Emma Carli emma.carli@outlook.com
#
# =============================================================================


#%% Clear variables

from IPython import get_ipython
get_ipython().magic('reset -f') 

#%% Import packages

import matplotlib.pyplot as plt
import numpy as np
from astropy.stats import sigma_clip
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
    start_time_GPS = float(file_raw[:-29])
    
    #if this file has already been cleaned, skip it and go to the next in raw_files
    if glob.glob('Cleaned_Data/'+str(start_time_GPS)+'_cleaned.dat') != []:
        print(str(start_time_GPS)+' already cleaned.')
        continue

    
    #%% Access the raw data
    handle_file_raw = open(file_raw, mode='rb') 
    data_raw = np.fromfile(handle_file_raw,'f4')
    
    #%% Crop the raw file to a length that is an integer number of minutes
    #so that later can sigma clip over one minute interval
    number_of_one_minute_intervals = int( np.floor( len(data_raw) / one_minute_in_datapoints ))
    data1 = data_raw[0: number_of_one_minute_intervals * one_minute_in_datapoints]
    
    #%% Remove median of whole dataset
    data2 = data1 - np.median(data1)
    
    #%% Median filter over a 1 second interval
    
    median_filter_1s = np.zeros(len(data2))
    number_of_one_second_intervals = number_of_one_minute_intervals * 60
    second_long_chunks_starting_points = np.linspace(0, len(data2) - one_second_in_datapoints , number_of_one_second_intervals , dtype='int')
    for second_long_chunk_start in second_long_chunks_starting_points :
    
        second_long_chunk_end =  second_long_chunk_start + one_second_in_datapoints
        
        median_filter_1s[second_long_chunk_start : second_long_chunk_end] = np.median(data2[second_long_chunk_start : second_long_chunk_end]) 

    data3 = data2 - median_filter_1s

# =============================================================================
#     #this was very long so made my own:
#     median_filter_1s = scipy.signal.medfilt(data2,kernel_size=one_second_in_datapoints-1) #kernel needs to be odd so removed 1 entry
# =============================================================================

    #%% Sigma clip over a 1 minute interval, since the drive jumps are < 1 min
    data_cleaned = np.zeros(len(data3))
    minute_long_chunks_starting_points = np.linspace(0, len(data3) - one_minute_in_datapoints , number_of_one_minute_intervals , dtype='int')
    for minute_long_chunk_start in minute_long_chunks_starting_points :
    
        minute_long_chunk_end =  minute_long_chunk_start + one_minute_in_datapoints
        
        sigma_masked_array = sigma_clip(data3[minute_long_chunk_start : minute_long_chunk_end], sigma=5, cenfunc='median', masked=True) #this is a NumPy MaskedArray object
        sigma_masked_array.set_fill_value(0.0)
        data_cleaned[minute_long_chunk_start : minute_long_chunk_end] = sigma_masked_array.filled()

    #%% Write the cleaned file
    
    #in the same way as a raw file, so can be opened the same way
    handle_file_cleaned = open('Cleaned_Data/'+start_time_GPS+'_cleaned.dat', 'wb')
    data_cleaned_binary = np.array(data_cleaned, 'f4')
    data_cleaned_binary.tofile(handle_file_cleaned)
    handle_file_cleaned.close()
    handle_file_raw.close()


    #%% Plot a comparison of the raw file and its cleaned version
    

    #%% If this file has already been plotted, skip it and go to the next in raw_files
    
    if glob.glob('Plots/'+str(start_time_GPS)+'_Compare_Cleaned_Raw*') != []:
        print(str(start_time_GPS)+' already plotted.')
        continue

    #%% Calculate values for axes and ticks
     
    #Raw dataset
    total_seconds_raw = number_of_one_second_intervals
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

