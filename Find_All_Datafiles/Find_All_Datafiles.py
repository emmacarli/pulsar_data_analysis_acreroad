# =============================================================================
# 
# This code finds all the raw and preprocessed files on ettus and plots their dates of recording.
# Author: Emma Carli 
# 
# =============================================================================

#%% Clear variables

from IPython import get_ipython
get_ipython().magic('reset -f') 

#%% Import packages

import matplotlib.pyplot as plt
import pysftp
import numpy as np
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

#%% Make lists of the preprocessed and raw files on ettus.

#initialise lists of the preprocessed and raw files on ettus
preproc_files = []
raw_files = []

with pysftp.Connection(host='ettus.astro.gla.ac.uk', username='astro') as sftp: #connect to ettus, no password as I am on the .authorised_keys list
    print('Connection successfully established.')
    sftp.cwd('/home/astro/pulsartelescope/data') #change working directory
    for file in sftp.listdir():
        if file.endswith('-PSRB0329-2ms-sampling-dd.dat'): #raw file name format
            raw_files.append(file)
        if file.endswith('-preproc.dat'): #preprocessed file name format
            preproc_files.append(file)

#%% Make lists of the recorded start time of the preprocessed and raw files on ettus, in GPS format. 

#initialise list of datafiles' GPS times from filenames
preproc_files_GPStimes = []
raw_files_GPStimes = []


for datafiles, datafiles_GPStimes in zip([preproc_files,raw_files],[preproc_files_GPStimes,raw_files_GPStimes]):
    for file in datafiles:
        if file.endswith('-PSRB0329-2ms-sampling-dd.dat'): #if raw
            datafiles_GPStimes.append(float(file[:-29]))
        if file.endswith('-preproc.dat'):
            datafiles_GPStimes.append(float(file[:-12])) #if preprocessed

#%% Make list of the recorded start time of the preprocessed and raw files on ettus,in ISO dates for plot ticks.

# =============================================================================
# 
# HERE THE TIME FORMAT HAS BEEN SET BUT NOT THE SCALE/TIME STANDARD. THIS IS NOT PRECISE -- BUT ONLY PLOTTING DATES SO THAT'S OK.
# 
# =============================================================================

#now convert the GPS times string lists into astropy time format
raw_files_GPStimes_astropy = Time(raw_files_GPStimes, format='gps') 
preproc_files_GPStimes_astropy = Time(preproc_files_GPStimes, format='gps')
#convert GPS start times of each datafile into date of recording for plotting
preproc_files_dateticks = Time(preproc_files_GPStimes_astropy, format='iso', out_subfmt='date')
raw_files_dateticks = Time(raw_files_GPStimes_astropy, format='iso', out_subfmt='date')

#%% Plot the dates of recording of each datafile on ettus

fig1 = plt.figure(figsize=(10,4))
ax1 = plt.gca()
ax1.plot_date(raw_files_dateticks.plot_date, np.zeros(len(raw_files_dateticks))+0.5, label='Raw files', marker='.', linestyle='none')
plt.draw()
ax1.plot_date(preproc_files_dateticks.plot_date, np.zeros(len(preproc_files_dateticks))+0.55, label='Preprocessed files', marker='.', linestyle='none') #plot preprocessed files just a bit above raw files
fig1.autofmt_xdate()  # orient date labels at a slant  
plt.draw()
ax1.set_ylim((0,1))
ax1.yaxis.set_major_locator(plt.NullLocator()) #remove y axis labels and ticks, as the height of the plotted dates are meaningless
ax1.legend()
ax1.set_title('Time of start of datafiles on ettus')

plt.savefig('Find_All_Datafiles.pdf') #comment out if want an interactive plot
plt.close() #comment out if want an interactive plot


