ticks_in_minutes = False #decide whether to label data in minutes or hours


# =============================================================================
# 
# This code cleans one raw pulsar data file and plots what happens to the data as it's cleaned.
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
fig1 = plt.figure()
ax1 = plt.gca()

    
#%% Which raw file do you want to clean and plot?

start_time_GPS = 1185851408.100563 #change date here
file_raw = str(start_time_GPS)+'-PSRB0329-2ms-sampling-dd.dat'
handle_file_raw = open('/home/emma/Desktop/Raw_Datafiles/'+file_raw, mode='rb') 
data_raw = np.fromfile(handle_file_raw,'f4')
#ax1.plot(data_raw, label='Raw data')
ax1.plot(data_raw, label='Raw data', linestyle = 'none',   marker='s', markersize=72/fig1.dpi, mec='None') #comment out depending on what you want on your plot
#using a square without border at the pixel size for a marker is a workaround using Matplotlib's pixel marker ',' which size cannot be increased in the legend.

#%% Crop the raw file to a length that is an integer number of minutes
#so that later can sigma clip over one minute interval
number_of_one_minute_intervals = int( np.floor( len(data_raw) / one_minute_in_datapoints ))
data1 = data_raw[0: number_of_one_minute_intervals * one_minute_in_datapoints]
#ax1.plot(data1, label='Cropped to integer number of minutes') #comment out depending on what you want on your plot

#%% Remove median of whole dataset
data2 = data1 - np.median(data1)
#ax1.plot(data2, label='Median subtracted') #comment out depending on what you want on your plot

#%% Median filter over a 1 second interval

median_filter_1s = np.zeros(len(data2))
number_of_one_second_intervals = number_of_one_minute_intervals * 60
second_long_chunks_starting_points = np.linspace(0, len(data2) - one_second_in_datapoints , number_of_one_second_intervals , dtype='int')
for second_long_chunk_start in second_long_chunks_starting_points :

    second_long_chunk_end =  second_long_chunk_start + one_second_in_datapoints
    
    median_filter_1s[second_long_chunk_start : second_long_chunk_end] = np.median(data2[second_long_chunk_start : second_long_chunk_end]) 

data3 = data2 - median_filter_1s
#ax1.plot(data3, label='One second median filtered') #comment out depending on what you want on your plot

# =============================================================================
#     #this was very long so made my own:
#     median_filter_1s = scipy.signal.medfilt(data2,kernel_size=one_second_in_datapoints-1) #kernel needs to be odd so removed 1 entry
# =============================================================================

#%% Sigma clip over a 1 minute interval, since the drive jumps are < 1 min
data4 = np.zeros(len(data3))
minute_long_chunks_starting_points = np.linspace(0, len(data3) - one_minute_in_datapoints , number_of_one_minute_intervals , dtype='int')
for minute_long_chunk_start in minute_long_chunks_starting_points :

    minute_long_chunk_end =  minute_long_chunk_start + one_minute_in_datapoints
    
    sigma_masked_array = sigma_clip(data3[minute_long_chunk_start : minute_long_chunk_end], sigma=5, cenfunc='median', masked=True) #this is a NumPy MaskedArray object
    sigma_masked_array.set_fill_value(0.0)
    data4[minute_long_chunk_start : minute_long_chunk_end] = sigma_masked_array.filled()
#ax1.plot(data4, label='One minute 5-sigma clip filtered')
ax1.plot(data4, label='Cleaned data', linestyle = 'none',   marker='s', markersize=72/fig1.dpi, mec='None') #comment out depending on what you want on your plot

#%% Add details to the finished plot

# =============================================================================
# 
# HERE THE TIME FORMAT HAS BEEN SET BUT NOT THE SCALE/TIME STANDARD. THIS IS NOT PRECISE -- BUT ONLY FOR A PLOT SO THAT'S OK.
# 
# =============================================================================
 
#convert the GPS time string  into astropy time format
start_time_GPS_astropy = Time(start_time_GPS, format='gps') 
start_time_ISO_astropy = Time(start_time_GPS_astropy, format='iso')


ax1.legend(markerscale=12,loc='upper right')
ax1.set_ylabel('Power (arbitrary units)')
ax1.set_title('Data cleaning steps on raw file starting '+start_time_ISO_astropy.value)

#%% Set x-axis and ticks

total_seconds = number_of_one_second_intervals
total_hours =  total_seconds / 3600
total_hours_rounded = np.ceil(total_hours)
total_hours_rounded_datapoints =total_hours_rounded*3600/sampling_period

major_ticks = np.linspace(0, total_hours_rounded_datapoints, num=total_hours_rounded+1) #set big ticks every hour
minor_ticks = np.linspace(0, total_hours_rounded_datapoints, num=((total_hours_rounded*60)+1)) #set small ticks every minute


if ticks_in_minutes == False:
    ax1.set_xticks(major_ticks)
    ax1.set_xticks(minor_ticks, minor=True)
    ax1.grid(which='minor', alpha=0.2)
    ax1.grid(which='major', alpha=0.5)
    ax1.set_xticklabels(np.linspace(0, total_hours_rounded, num=total_hours_rounded+1))
    ax1.set_xlabel('Time since start (hours)')
else:
   ax1.set_xticks(minor_ticks)
   ax1.grid(which='major', alpha=0.5)
   ax1.set_xticklabels(np.linspace(0, total_hours_rounded*60, num=(total_hours_rounded*60)+1))
   ax1.set_xlabel('Time since start (minutes)')

handle_file_raw.close()

