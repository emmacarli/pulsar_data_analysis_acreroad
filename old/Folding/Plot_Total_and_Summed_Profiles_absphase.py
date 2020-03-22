#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 14:48:13 2020

@author: emma
"""

import numpy as np
import glob
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

template_profile = np.genfromtxt('/home/emma/Desktop/pulsardataprep_acreroad/PRESTO_Test/TOA_find_test/Jodrell_Template_Profile_I-Q.txt')
phase_bins = template_profile[:,0]

template_profile =  template_profile[:,1]/np.max(template_profile)


FFTFIT_results = np.genfromtxt('FFTFIT_results.txt')
SNRs = FFTFIT_results[:,3] #load the folded profiles' SNRs



profile_files_paths = np.array(glob.glob('/home/emma/Desktop/pulsardataprep_acreroad/Folding/PRESTO_Folded_Profiles/*.bestprof'))

SNR_cutoffs = np.linspace(1,7,25) #create a range of SNR cutoffs which will select profiles to be added in the total profile


mean_residuals = []
max_residuals = []

for SNR_cutoff in SNR_cutoffs:
    
    total_profile = np.zeros(512)

    for profile_file_path, SNR in zip(profile_files_paths[SNRs>SNR_cutoff] , SNRs[SNRs>SNR_cutoff]):
        profile = np.genfromtxt(profile_file_path, skip_header=26)[:,1]
        
        total_profile += profile*SNR
        
    
    #%%
    
    
    total_profile = np.roll(total_profile, int(len(total_profile)/2))
    total_profile -= np.median(total_profile)
    total_profile =  resample(total_profile, len(template_profile))
    total_profile =  total_profile/np.max(total_profile)
    
    residuals = template_profile - total_profile
    mean_residuals.append(np.mean(residuals))
    max_residuals.append(np.max(residuals))
    
    
    #%%
    
# =============================================================================
#     fig1 = plt.figure()
#     ax1=plt.gca()
#     plt.step(phase_bins, total_profile, linewidth=0.5, color='black', label='Total Profile')
#     plt.step(phase_bins, template_profile, linewidth=0.5, color='red', label='Template Profile')
#     plt.legend()
#     ax1.set_title('Total profile comparison SNR cutoff '+str(SNR_cutoff))
#     ax1.set_xlabel("Phase")
#     ax1.set_ylabel("Relative intensity")
#     plt.savefig('Total_Profile_Comparison_absphase_SNR_cutoff_'+str(SNR_cutoff)+'.pdf') 
# 
# #SAVE BEST PROFILE
#     plt.close()
# =============================================================================


fig2, ax2 = plt.subplots(2,1, figsize=(11,10))
ax2[0].plot(SNR_cutoffs, mean_residuals, marker='o', markersize=3, linestyle='none', color='black')
ax2[0].set_ylabel("Mean residuals (relative intensity)")
ax2[1].plot(SNR_cutoffs, max_residuals, marker='o', markersize=3, linestyle='none', color='black')
ax2[1].set_xlabel("SNR cutoff")
ax2[1].set_ylabel("Maximum residuals (relative intensity)")
fig2.suptitle('Evolution of residuals with SNR cutoff')
plt.savefig('Evolution_of_total_profile_residuals_with_SNR.pdf') 

plt.close()

    
