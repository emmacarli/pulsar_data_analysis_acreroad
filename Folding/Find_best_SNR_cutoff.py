# =============================================================================
# 
# This code finds the best SNR cutoff.
# To add your own paths, replace all the 'path_to_...' variables.
# Author: Emma Carli
#
# =============================================================================


#%% Clear variables

from IPython import get_ipython
get_ipython().magic('reset -f') 

#%% Import packages

import matplotlib.pyplot as plt
import glob
import numpy as np
import subprocess
import re
import time
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


#%% Start a log and define paths

log_handle = open('Find_best_SNR_cutoff.log', 'w')
path_to_folded_profiles =  '/home/emma/Desktop/pulsardataprep_acreroad/Folding/PRESTO_Folded_Profiles/'
path_to_template_profile = '/home/emma/Desktop/pulsardataprep_acreroad/Folding/Jodrell_Template_Profile_I-Q_PRESTO_Gaussian_fit.gaussians' #this was generated using PRESTO's pygaussfit.py on the Jodrell Bank template for this pulsar


#%% Here change variables to test the analysis

number_of_profile_bins = '512' #this is the number of phase bins in the folded profiles and in the total profile, it has to be a power of two!
#otherwise, for folding, PRESTO defaults to the number of sampling bins which correspond to one folded period, in our case about 64, and for the total profile, it defaults to 128.

#%%
#to find floats, integers, and numbers with exponents in output files, we need to use regular expressions
#this one was taken from https://stackoverflow.com/questions/4703390/how-to-extract-a-floating-number-from-a-string , second answer
regexp_numeric_pattern = r'[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
#this expression needs compiled by regexp
any_number = re.compile(regexp_numeric_pattern, re.VERBOSE)

#%% SNR definitions

FFTFIT_results = np.genfromtxt('FFTFIT_results.txt')
SNRs = FFTFIT_results[:,2] #load the folded profiles' SNRs
total_profiles_SNRs = [] #initialise list of total summed profiles SNRs
SNR_cutoffs = [] #create a range of SNR cutoffs which will select profiles to be added in the total profile
SNR_cutoffs.extend(np.linspace(1,3.5,6))
SNR_cutoffs.extend(np.linspace(4,6,11))
SNR_cutoffs.extend(np.linspace(6.5,7.5,3))

for SNR_cutoff in SNR_cutoffs:
    
    #%% Create a total profile
    
    prepfold_files_paths = sorted(glob.glob(path_to_folded_profiles+'/*.pfd'))
    prepfold_files_paths = np.ma.masked_where(SNRs<SNR_cutoff, prepfold_files_paths)
    prepfold_files_paths = prepfold_files_paths[~prepfold_files_paths.mask]
    prepfolds_filenames_list_handle = open('prepfolds_filenames_list.txt', 'w')
    for prepfold_file_path in prepfold_files_paths:
            prepfolds_filenames_list_handle.write("%s\n" % prepfold_file_path)
    
    PRESTO_totalprofile_command = 'sum_profiles.py -n '+number_of_profile_bins+' -g '+path_to_template_profile+' prepfolds_filenames_list.txt'
    
    log_handle.write('PRESTO total profile command: ' + PRESTO_totalprofile_command+'\n')
    
    terminal_totalprofile_run = subprocess.Popen(PRESTO_totalprofile_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    time.sleep(2) #give it some computing time before pressing enter
    output_totalprofile_run = terminal_totalprofile_run.communicate(input=b'\n \n \n \n \n \n \n')[0] #this program needs to have enter pressed twice  

    log_handle.write(output_totalprofile_run.decode('utf-8')+'\n')
    total_profile = np.genfromtxt('sum_profiles.bestprof')
    
    fig1 = plt.figure()
    ax1 = plt.gca()
    plt.step(total_profile[:,0],total_profile[:,1], linewidth=0.5, color='black')
    ax1.set_xlabel('Pulse phase bins')
    ax1.set_ylabel('Relative flux')
    ax1.set_title('Total summed profile with SNR cutoff'+str(SNR_cutoff))
    plt.savefig('Total_Profile_SNR_cutoff_'+str(SNR_cutoff)+'.pdf') 
    plt.close()

#%%
    

    
    for i in range(1,100):
        number_of_lines_from_end = str(i)
        line_bytes = subprocess.check_output(['tail', '-'+number_of_lines_from_end, 'Find_best_SNR_cutoff.log'])
        line = line_bytes.decode(encoding='utf-8')
        if 'Summed profile approx SNR' in line:
            total_profile_SNR = any_number.findall(line)
            break

    total_profiles_SNRs.append(float(total_profile_SNR[0]))
    
    prepfolds_filenames_list_handle.close()
    


#%% Clean up
os.remove('prepfolds_filenames_list.txt')
os.remove('sum_profiles.bestprof')
log_handle.close()



fig2 = plt.figure()
ax2 = plt.gca()
plt.plot(SNR_cutoffs, total_profiles_SNRs, linestyle='none', marker='o', markerfacecolor='black', markeredgecolor='black')   
ax2.set_xlabel('SNR cutoff')
ax2.set_ylabel('Total summed profile SNR')
plt.savefig('Total_profile_SNR_evolution_with_cutoffs.pdf') 
plt.close()
