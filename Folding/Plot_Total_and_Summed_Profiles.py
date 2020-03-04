import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import resample


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

#%%

template_profile = np.genfromtxt('/home/emma/Desktop/pulsardataprep_acreroad/PRESTO_Test/TOA_find_test/Jodrell_Template_Profile_I-Q.txt')
template_profile =  template_profile[:,1]/np.max(template_profile)
total_profile = np.genfromtxt('/home/emma/Desktop/pulsardataprep_acreroad/Folding/sum_profiles_SNR_cutoff_5.bestprof')
total_profile =  total_profile[:,1]
total_profile = np.roll(total_profile, np.argmax(total_profile))
total_profile =  resample(total_profile, len(template_profile))
total_profile =  total_profile/np.max(total_profile)

#%%

fig1 = plt.figure()
ax1=plt.gca()
plt.step(range(443), total_profile, linewidth=0.5, color='black', label='Total Profile')
plt.step(range(443), template_profile, linewidth=0.5, color='red', label='Template Profile')
plt.legend()
ax1.set_title("Total profile comparison")
ax1.set_xlabel("Phase bins")
ax1.set_ylabel("Relative intensity")
plt.savefig('Total_Profile_Comparison.pdf') 
plt.close()

