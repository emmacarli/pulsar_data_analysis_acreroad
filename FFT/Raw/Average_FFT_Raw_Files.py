# =============================================================================
# 
# This code plots an average FFT transform of all raw datafiles, cropped at 4 hours.
# Author: Emma Carli emma.carli@outlook.com
#
# =============================================================================


#%% Clear variables

from IPython import get_ipython
get_ipython().magic('reset -f') 

#%% Import packages

import numpy as np
import matplotlib.pyplot as plt
import glob

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
four_hours_in_datapoints = int((4 * 3600)/sampling_period)

fft_total = np.zeros(int((four_hours_in_datapoints/2)+1)) #initialise empty FFT
fft_total_time_axis = np.fft.rfftfreq(four_hours_in_datapoints,sampling_period) 
raw_files = glob.glob('/home/emma/Desktop/Raw_Datafiles/*-PSRB0329-2ms-sampling-dd.dat') #list of raw files on my computer
short_files = 0 #initialise counter for number of raw datafiles shorter than 4 hours

#%% Compute the mean FFT

for file_raw in raw_files: #go through each raw file
    
    handle_file_raw = open(file_raw, mode='rb') 
    data_raw = np.fromfile(handle_file_raw,'f4')
    sample_points = len(data_raw)
    
    if sample_points < four_hours_in_datapoints : #skip the file if it is shorter than four hours
        short_files = short_files+1 #count a short raw file
        continue
   
    fft_raw = np.fft.rfft(data_raw[:four_hours_in_datapoints]) #perform the FFT on the raw file
    fft_total =  (fft_total + fft_raw) /2 #average the FFTs

    handle_file_raw.close()

#%% Plot the result

print(str(short_files)+' raw file(s) shorter than 4 hours and not used in FFT.')

fig1=plt.figure()
ax1=plt.gca()
ax1.plot(fft_total_time_axis, np.abs(fft_total)**2, linewidth=0.7, color='black')
ax1.set_ylabel('Power (arbitrary units)')
ax1.set_xlabel('Frequency (Hz)')
ax1.set_title('Averaged FFT of all raw files')
ax1.set_yscale('log')

#%% Save or load the result
#np.savez('mean_raw_fft.npz',fft_total=fft_total, fft_total_time_axis=fft_total_time_axis)
#meanfft = np.load('mean_raw_fft.npz')
#fft_total = meanfft[fft_total]
#fft_total_time_axis = meanfft[fft_total_time_axis]
