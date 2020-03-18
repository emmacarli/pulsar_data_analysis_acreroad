# =============================================================================
# 
# This code cleans all raw pulsar data files. 
# Author: Emma Carli 
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
from progress.bar import Bar

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

path_to_raw_files = '/home/emma/Desktop/Raw_Datafiles/'
path_to_cleaned_files = '/home/emma/Desktop/Cleaned_Data/'

#%% Clean data


#Make a list of raw files' paths in my computer
raw_files = glob.glob(path_to_raw_files+'*-PSRB0329-2ms-sampling-dd.dat') #this suffix was added at recording

bar = Bar('Processing...', max=len(raw_files), fill='\U0001F4E1', suffix = '%(percent).1f%% - %(eta)ds') #create a progress bar
bar.check_tty = False

# Go through each raw file
for raw_file in raw_files: 
    start_time_GPS = float(raw_file[len(path_to_raw_files):-len('-PSRB0329-2ms-sampling-dd.dat')]) #the start of the filename gives the beginning of the recording time in GPS format
    bar.next()
      
    #If this file has already been cleaned, skip it and go to the next in raw_files
    if glob.glob(path_to_cleaned_files+str(start_time_GPS)+'_cleaned.dat') != []:
        print(str(start_time_GPS)+' already cleaned.')
        continue
    
    # Load in the raw data
    handle_raw_file = open(raw_file, mode='rb') 
    data_raw = np.fromfile(handle_raw_file,'f4')
    
    # Crop the raw file to a length that is an integer number of minutes
    # so that can perform operations over one minute / one second intervals
    number_of_one_minute_intervals = int( np.floor( len(data_raw) / one_minute_in_datapoints ))
    data1 = data_raw[0: number_of_one_minute_intervals * one_minute_in_datapoints] #step 1 of cleaning
    
    # Remove median of whole dataset
    data2 = data1 - np.median(data1) #step 2 of cleaning
    
    # Median removal over 1 second intervals (not a proper filter with sliding window!)
    median_filter_1s = np.zeros(len(data2))
    number_of_one_second_intervals = number_of_one_minute_intervals * 60

    second_long_chunks_starting_points = np.linspace(0, len(data2) - one_second_in_datapoints , number_of_one_second_intervals , dtype='int')

    for second_long_chunk_start in second_long_chunks_starting_points :
        second_long_chunk_end =  second_long_chunk_start + one_second_in_datapoints
        
        median_filter_1s[second_long_chunk_start : second_long_chunk_end] = np.median(data2[second_long_chunk_start : second_long_chunk_end]) 

    data3 = data2 - median_filter_1s #step 3 of cleaning

    # Sigma clip over 1 minute intervals, since the drive jumps are < 1 min
    data4 = np.zeros(len(data3))
    
    minute_long_chunks_starting_points = np.linspace(0, len(data3) - one_minute_in_datapoints , number_of_one_minute_intervals , dtype='int')
    
    for minute_long_chunk_start in minute_long_chunks_starting_points :
        minute_long_chunk_end =  minute_long_chunk_start + one_minute_in_datapoints
        
        sigma_masked_array = sigma_clip(data3[minute_long_chunk_start : minute_long_chunk_end], sigma=5, cenfunc='median', masked=True) #this is a NumPy MaskedArray object
        sigma_masked_array.set_fill_value(0.0)
        
        data4[minute_long_chunk_start : minute_long_chunk_end] = sigma_masked_array.filled()
        
    # STD divide to whiten data over a 1 minute interval
        data_cleaned = np.zeros(len(data4))
        
        for minute_long_chunk_start in minute_long_chunks_starting_points :
    
            minute_long_chunk_end =  minute_long_chunk_start + one_minute_in_datapoints
            
            if np.std(data4[minute_long_chunk_start : minute_long_chunk_end]) != 0 :
                data_cleaned[minute_long_chunk_start : minute_long_chunk_end] = data4[minute_long_chunk_start : minute_long_chunk_end]/np.std(data4[minute_long_chunk_start : minute_long_chunk_end]) #4th and last step of cleaning
        
    # Write the cleaned file in the same way as a raw file, so can be opened the same way
    handle_file_cleaned = open(path_to_cleaned_files+str(start_time_GPS)+'_cleaned.dat', 'wb')
    data_cleaned_binary = np.array(data_cleaned, 'f4')
    data_cleaned_binary.tofile(handle_file_cleaned)
    
    # Close files
    handle_file_cleaned.close()
    handle_raw_file.close()


bar.finish()