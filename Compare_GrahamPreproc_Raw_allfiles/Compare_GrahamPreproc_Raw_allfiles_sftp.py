# =============================================================================
# 
# This code plots raw data and data preprocessed using Graham's routine.
# PDFs are useful to save all the plots but interactive plots can be looked at with more precision, although individually.
# This code does not need to be run from ettus. It must be run on campus or using a VPN.
# Author: Emma Carli emma.carli@outlook.com
#
# =============================================================================


#%% Clear variables

from IPython import get_ipython
get_ipython().magic('reset -f') 

#%% Import packages

import numpy as np
import matplotlib.pyplot as plt
import pysftp
from astropy.time import Time
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


#%% Make lists of the preprocessed and raw files on ettus.

#initialise lists of the preprocessed and raw files on ettus
preproc_files = []
raw_files = []

sftp = pysftp.Connection(host='ettus.astro.gla.ac.uk', username='astro') #connect to ettus, no password as I am on the .authorised_keys list
print('Connection successfully established.')
sftp.cwd('/home/astro/pulsartelescope/data') #change working directory
for file in sftp.listdir():
    if file.endswith('-PSRB0329-2ms-sampling-dd.dat'): #raw file name format
        raw_files.append(file)
    if file.endswith('-preproc.dat'): #preprocessed file name format
        preproc_files.append(file)

#%% Set known data rates

sampling_period = 2e-3 #2 ms
sampling_rate = 1/sampling_period

for file_preproc in preproc_files:
    
    start_time_GPS = float(file_preproc[:-12])

    #if this file has already been plotted, skip it and go to the next in preproc_files
    if os.path.exists(str(start_time_GPS)+'_GrahamPreproc.pdf') or os.path.exists(str(start_time_GPS)+'_Compare_GrahamPreproc_Raw.pdf'):
        continue
    
    #%% Upload the data file
    print('Downloading '+file_preproc+'...')
    sftp.get(file_preproc) #downloads the preprocessed file in the current working directory
    print(file_preproc+' downloaded.')
    
    
    #Preprocessed data
    handle_file_preproc = open(file_preproc, mode='rb')
    data_preproc = np.fromfile(handle_file_preproc,'f4')
    
    #Raw data
    file_raw = str(start_time_GPS)+'-PSRB0329-2ms-sampling-dd.dat'
    try: 
        print('Downloading '+file_raw+'...')
        sftp.get(file_raw) #downloads the raw file in the current working directory
        print(file_raw+' downloaded.')
        f_raw = open(file_raw, mode='rb')
        raw_file_exists = True
    except FileNotFoundError:
        raw_file_exists = False  
        print('Raw file does not exist.')
    
    if raw_file_exists == True:
        data_raw = np.fromfile(f_raw, 'f4')
    
    #%% Calculate values for axes and ticks
    
    #Preprocessed dataset
    total_seconds_preproc = len(data_preproc)*sampling_period #total seconds in dataset
    total_hours_preproc =  total_seconds_preproc / 3600 #total hours in dataset
    total_hours_rounded_preproc = np.ceil(total_hours_preproc) #total rounded hours in dataset
    total_hours_rounded_datapoints_preproc = total_hours_rounded_preproc*3600/sampling_period #how many datapoints in total rounded hours in dataset
    
    #Raw dataset
    if raw_file_exists == True:
        total_seconds_raw = len(data_raw)*sampling_period
        total_hours_raw =  total_seconds_raw / 3600
        total_hours_raw_rounded = np.ceil(total_hours_raw)
        total_hours_rounded_datapoints_raw =total_hours_raw_rounded*3600/sampling_period
        0
    
    #%% Set axes and ticks
    
    #Preprocessed dataset
    major_ticks_preproc = np.linspace(0, total_hours_rounded_datapoints_preproc, num=total_hours_rounded_preproc+1) #set big ticks every hour
    minor_ticks_preproc = np.linspace(0, total_hours_rounded_datapoints_preproc, num=((total_hours_rounded_preproc*60)+1)) #set small ticks every minute
    
    #Raw dataset
    if raw_file_exists == True:
        major_ticks_raw = np.linspace(0, total_hours_rounded_datapoints_raw, num=total_hours_raw_rounded+1) #set big ticks every hour
        minor_ticks_raw = np.linspace(0, total_hours_rounded_datapoints_raw, num=((total_hours_raw_rounded*60)+1)) #set small ticks every minute
    
    #%% Plot raw and preprocessed files
    
    fig1 = plt.figure()
    
    if raw_file_exists == True: #if there is a raw file corresponding to the preprocessed one, make a plot comparing the two.
        #Preprocessed dataset
        fig1_top = fig1.add_subplot(2,1,1)
        fig1_top.plot(data_preproc, color='black',  marker='None', linewidth=0.05) 
        fig1_top.set_ylabel('Power (arbitrary units)')
        fig1_top.set_xticks(major_ticks_preproc)
        fig1_top.set_xticks(minor_ticks_preproc, minor=True)
        fig1_top.grid(which='minor', alpha=0.2)
        fig1_top.grid(which='major', alpha=0.5)
        fig1_top.set_xticklabels(np.linspace(0, total_hours_rounded_preproc, num=total_hours_rounded_preproc+1))
        fig1_top.set_title('Preprocessed Data')
        
        #Raw dataset
        fig1_bottom = fig1.add_subplot(2,1,2)
        fig1_bottom.plot(data_raw, color='black', marker='None', linewidth=0.05) 
        fig1_bottom.set_xlabel('Time (hours)')
        fig1_bottom.set_ylabel('Power (arbitrary units)')
        fig1_bottom.set_xticks(major_ticks_raw)
        fig1_bottom.set_xticks(minor_ticks_raw, minor=True)
        fig1_bottom.grid(which='minor', alpha=0.2)
        fig1_bottom.grid(which='major', alpha=0.5)
        fig1_bottom.set_xticklabels(np.linspace(0, total_hours_raw_rounded, num=total_hours_raw_rounded+1))
        fig1_bottom.set_title('Raw data')
        
        # =============================================================================
        # 
        # HERE THE TIME FORMAT HAS BEEN SET BUT NOT THE SCALE/TIME STANDARD. THIS IS NOT PRECISE -- BUT ONLY FOR A PLOT SO THAT'S OK.
        # 
        # =============================================================================
        
        #now convert the GPS time string  into astropy time format
        start_time_GPS_astropy = Time(start_time_GPS, format='gps') 
        start_time_ISO_astropy = Time(start_time_GPS_astropy, format='iso')
        
        
        fig1.suptitle('Start of recording: ' + start_time_ISO_astropy.value)
        plt.subplots_adjust(hspace=0.5)
        
        
        plt.savefig(str(start_time_GPS)+'_Compare_GrahamPreproc_Raw.pdf') 
        
    else: #if there is no raw file,  plot the preprocessed one on its own.
        ax1 = plt.gca()
        ax1.plot(data_preproc, color='black',  marker='None', linewidth=0.05) 
        ax1.set_ylabel('Power (arbitrary units)')
        ax1.set_xticks(major_ticks_preproc)
        ax1.set_xticks(minor_ticks_preproc, minor=True)
        ax1.set_xlabel('Time (hours)')
        ax1.grid(which='minor', alpha=0.2)
        ax1.grid(which='major', alpha=0.5)
        ax1.set_xticklabels(np.linspace(0, total_hours_rounded_preproc, num=total_hours_rounded_preproc+1))
        
        # =============================================================================
        # 
        # HERE THE TIME FORMAT HAS BEEN SET BUT NOT THE SCALE/TIME STANDARD. THIS IS NOT PRECISE -- BUT ONLY FOR A PLOT SO THAT'S OK.
        # 
        # =============================================================================
        
        #now convert the GPS time string  into astropy time format
        start_time_GPS_astropy = Time(start_time_GPS, format='gps') 
        start_time_ISO_astropy = Time(start_time_GPS_astropy, format='iso')
        
        
        ax1.set_title('Preprocessed Data, Start of recording: ' + start_time_ISO_astropy.value)
        
        plt.savefig(str(start_time_GPS)+'_GrahamPreproc.pdf') 
        

    os.remove(file_preproc)
    os.remove(file_raw) #sftp creates an empty file when trying download even if raw file does not exist on ettus
    plt.close() #comment out if want an interactive plot
    print('File(s) plotted and deleted.')

sftp.close()
