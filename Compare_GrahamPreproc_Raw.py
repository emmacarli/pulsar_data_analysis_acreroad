# =============================================================================
# 
# This code plots raw data and data preprocessed using Graham's routine.
# PDFs are useful to save all the plots but interactive plots can be looked at with more precision, although individually.
# Author: Emma Carli
# =============================================================================
#

#%% Clear variables

from IPython import get_ipython
get_ipython().magic('reset -f') 

#%% Import packages

import numpy as np
import matplotlib.pyplot as plt

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

#%% Set known data rates

sampling_period = 2e-3 #2 ms
sampling_rate = 1/sampling_period

#%% Upload the data files

f_raw = open('1183079651.114455-PSRB0329-2ms-sampling-dd.dat', mode='rb')
f = open('1183079651.114455-preproc.dat', mode='rb')
data = np.fromfile(f,'f4')
data_raw = np.fromfile(f_raw, 'f4')

#%% Calculate values for axes and ticks

#Preprocessed dataset
total_seconds = len(data)*sampling_period #total seconds in dataset
total_hours =  total_seconds / 3600 #total hours in dataset
total_hours_rounded = np.ceil(total_hours) #total rounded hours in dataset
total_hours_rounded_datapoints = total_hours_rounded*3600/sampling_period #how many datapoints in total rounded hours in dataset

#Raw dataset
total_seconds_raw = len(data_raw)*sampling_period
total_hours_raw =  total_seconds_raw / 3600
total_hours_raw_rounded = np.ceil(total_hours_raw)
total_hours_rounded_datapoints_raw =total_hours_raw_rounded*3600/sampling_period
0

#%% Set axes and ticks

#Preprocessed dataset
major_ticks = np.linspace(0, total_hours_rounded_datapoints, num=total_hours_rounded+1) #set big ticks every hour
minor_ticks = np.linspace(0, total_hours_rounded_datapoints, num=((total_hours_rounded*60)+1)) #set small ticks every minute

#Raw dataset
major_ticks_raw = np.linspace(0, total_hours_rounded_datapoints_raw, num=total_hours_raw_rounded+1) #set big ticks every hour
minor_ticks_raw = np.linspace(0, total_hours_rounded_datapoints_raw, num=((total_hours_raw_rounded*60)+1)) #set small ticks every minute

#%% Plot raw and preprocessed files

fig1 = plt.figure()

#Preprocessed dataset
fig1_top = fig1.add_subplot(2,1,1)
fig1_top.plot(data, color='black',  marker='None', linewidth=0.05) #comment out to get an interactive plot.
#fig1_top.plot(data, color='black',  linestyle='none', marker=',') #uncomment to get an interactive plot. can't plot individual points in a pdf, it makes it too large to handle. make sure to comment out savefig and close, too.
fig1_top.set_ylabel('Power (arbitrary units)')
fig1_top.set_xticks(major_ticks)
fig1_top.set_xticks(minor_ticks, minor=True)
fig1_top.grid(which='minor', alpha=0.2)
fig1_top.grid(which='major', alpha=0.5)
fig1_top.set_xticklabels(np.linspace(0, total_hours_rounded, num=total_hours_rounded+1))
fig1_top.set_title('Preprocessed Data')

#Raw dataset
fig1_bottom = fig1.add_subplot(2,1,2)
fig1_bottom.plot(data_raw, color='black', marker='None', linewidth=0.05) #comment out to get an interactive plot.
#fig1_bottom.plot(data_raw, color='black',  linestyle='none', marker=',') #uncomment to get an interactive plot. can't plot individual points in a pdf, it makes it too large to handle.  make sure to comment out savefig and close, too.
fig1_bottom.set_xlabel('Time (hours)')
fig1_bottom.set_ylabel('Power (arbitrary units)')
fig1_bottom.set_xticks(major_ticks_raw)
fig1_bottom.set_xticks(minor_ticks_raw, minor=True)
fig1_bottom.grid(which='minor', alpha=0.2)
fig1_bottom.grid(which='major', alpha=0.5)
fig1_bottom.set_xticklabels(np.linspace(0, total_hours_raw_rounded, num=total_hours_raw_rounded+1))
fig1_bottom.set_title('Raw data')

plt.savefig('Compare_Preproc_Raw.pdf') #comment out if want an interactive plot
plt.close() #comment out if want an interactive plot
