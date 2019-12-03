# =============================================================================
# 
# This code plots an average FFT transform of all cleaned datafiles, cropped at 4 hours.
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
cleaned_files = glob.glob('/home/emma/Desktop/pulsardataprep_acreroad/Clean_Data/Cleaned_Data/*.dat') #list of cleaned files on my computer
short_files = 0 #initialise counter for number of cleaned datafiles shorter than 4 hours

#%% Compute the mean FFT

for file_cleaned in cleaned_files: #go through each cleaned file
    
    handle_file_cleaned = open(file_cleaned, mode='rb') 
    data_cleaned = np.fromfile(handle_file_cleaned,'f4')
    sample_points = len(data_cleaned)
    
    if sample_points < four_hours_in_datapoints : #skip the file if it is shorter than four hours
        short_files = short_files+1 #count a short cleaned file
        continue
   
    fft_cleaned = np.fft.rfft(data_cleaned[:four_hours_in_datapoints]) #perform the FFT on the cleaned file
    fft_total =  (fft_total + fft_cleaned) /2 #average the FFTs

    handle_file_cleaned.close()

#%% Plot the result

print(str(short_files)+' cleaned file(s) shorter than 4 hours and not used in FFT.')

fig1=plt.figure()
ax1=plt.gca()
ax1.plot(fft_total_time_axis, np.abs(fft_total)**2, linewidth=0.7, color='black')
ax1.set_ylabel('Power (arbitrary units)')
ax1.set_xlabel('Frequency (Hz)')
ax1.set_title('Averaged FFT of all cleaned files')
ax1.set_yscale('log')

#%% Save or load the result
#np.savez('mean_cleaned_fft.npz',fft_total=fft_total, fft_total_time_axis=fft_total_time_axis)
#meanfft = np.load('mean_cleaned_fft.npz')
#fft_total = meanfft[fft_total]
#fft_total_time_axis = meanfft[fft_total_time_axis]

#%% Some experimentation with looking at the peaks

# =============================================================================
# entries = find_peaks(np.abs(fft_total**2), threshold=1e8, distance=1000)[0]
# frequencies =  fft_total_time_axis[entries]
# plt.plot(frequencies, linestyle='none', marker='.')
# plt.plot(frequencies, np.zeros(len(frequencies)), linestyle='none', marker='.')
#
# =============================================================================
