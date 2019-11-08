# =============================================================================
# This code plots preprocessed and raw data.
# Author: Emma Carli
# =============================================================================


#%%
from IPython import get_ipython
get_ipython().magic('reset -f') 

#%%
import numpy as np
import matplotlib.pyplot as plt

#%%

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


#%%

sampling_period = 2e-3
sampling_rate = 1/sampling_period



#%%


f_raw = open('/home/emma/OneDrive/Work/Masters_project/Pulsar_Telescope/1183079651.114455-PSRB0329-2ms-sampling-dd.dat', mode='rb')
f = open('/home/emma/OneDrive/Work/Masters_project/Pulsar_Telescope/1183079651.114455-preproc.dat', mode='rb')
data = np.fromfile(f,'f4')
data_raw = np.fromfile(f_raw, 'f4')

#%%

total_seconds = len(data)*sampling_period
total_hours =  total_seconds / 3600
total_hours_rounded = np.round(total_hours) #in case recording is not exactly 4 hours

total_seconds_raw = len(data_raw)*sampling_period
total_hours_raw =  total_seconds_raw / 3600
total_hours_raw_rounded = np.round(total_hours_raw) #in case recording is not exactly 4 hours

#%%

fig1 = plt.figure()
#####TICKS ARE WRONG

fig1_top = fig1.add_subplot(2,1,1)
fig1_top.plot(data, color='black')
fig1_top.set_ylabel('Power (arbitrary units)')
fig1_top.set_xticks(np.linspace(0,len(data),num=5))
fig1_top.set_xticklabels(np.linspace(0,total_hours_rounded,5))
fig1_top.set_title('Preprocessed Data')

fig1_bottom = fig1.add_subplot(2,1,2)
fig1_bottom.plot(data_raw, color='black')
fig1_bottom.set_xlabel('Time (hours)')
fig1_bottom.set_ylabel('Power (arbitrary units)')
fig1_bottom.set_xticks(np.linspace(0,len(data_raw),num=5))
fig1_bottom.set_xticklabels(np.linspace(0,total_hours_raw_rounded,5))
fig1_bottom.set_title('Raw data')

plt.savefig('Compare_Preproc_Raw.pdf')
plt.close()