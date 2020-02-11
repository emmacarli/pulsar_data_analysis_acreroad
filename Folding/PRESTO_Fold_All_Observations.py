# =============================================================================
# 
# This code folds all the observations using PRESTO.
# To add your own paths, replace all the 'path_to_...' variables.
# Author: Emma Carli
#
# =============================================================================


#%% Clear variables

from IPython import get_ipython
get_ipython().magic('reset -f') 

#%% Import packages

import matplotlib.pyplot as plt
from astropy.time import Time
import glob
import numpy as np
import subprocess
from My_Functions.update_text import update_text
from shutil import copyfile
import os
from progress.bar import Bar
import re
import time


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

#%% Here change variables to test the analysis

number_of_profile_bins = '1024' #this is the number of phase bins in the folded profiles and in the total profile, it has to be a power of two!
#otherwise, for folding, PRESTO defaults to the number of sampling bins which correspond to one folded period, in our case about 64, and for the total profile, it defaults to 128.
absphase = '-absphase' #empty the string if don't want to fold in absolute phase

#%% Start a log
log_handle = open('PRESTO_Fold_All_Observations.log', 'w')


#%% Set known variables

sampling_period = 2e-3 #2 ms
one_second_in_datapoints = int(1/sampling_period) #500 datapoints = 1 second of recording
one_minute_in_datapoints= one_second_in_datapoints * 60

#%% Find out time span of the available observations

path_to_cleaned_files = '/home/emma/Desktop/Cleaned_Data'
cleaned_files = sorted(glob.glob(path_to_cleaned_files+'/*_cleaned.dat'))
minimum_GPS_time = Time(float(cleaned_files[0][32:-12]), format='gps') #this is the first date at which I start having observations, extracted from the file name of the ordered cleaned files.
log_handle.write('The observations start on ' + minimum_GPS_time.iso+'\n')
maximum_GPS_time = Time(float(cleaned_files[len(cleaned_files)-1][32:-12]), format='gps') #this is the last observation date
log_handle.write('The observations end on ' + maximum_GPS_time.iso+'\n')
observations_span = maximum_GPS_time - minimum_GPS_time
log_handle.write('The observations span '+str(observations_span.jd)+' days. \n')
log_handle.write('\n \n \n \n') 

    #If try to generate TEMPO polycos for the whole observations span (in my case, a year), Nspan too small error even for hundreds of hours:
    #'tempo  -ZOBS=AR -ZFREQ=407.5 -ZTOBS='+str(np.ceil(observations_span.jd*24))+' -ZSTART='+str(np.floor(minimum_GPS_time.mjd))+'  -ZNCOEFF=15 -ZSPAN=1000H -f B0329+54.par'

#%% Create a file in which to write the results of this script

PRESTO_TOAs_handle = open('PRESTO_TOAs.txt' , 'w')
path_to_folded_profiles =  '/home/emma/Desktop/pulsardataprep_acreroad/Folding/PRESTO_Folded_Profiles/'


#%%Loop through observations


bar = Bar('Processing', max=len(cleaned_files), suffix = '%(percent).1f%% - %(eta)ds') #create a progress bar
bar.check_tty = False

for file_cleaned in cleaned_files:
    
    
    #%% Find out the start time and length of the observation
    
    
    start_time_GPS = float(file_cleaned[32:-12])
    start_time_GPS_astropy = Time(start_time_GPS, format='gps') 
    log_handle.write('Observation starting on GPS time '+str(start_time_GPS)+' i.e. '+str(start_time_GPS_astropy.iso)+'\n')
    handle_file_cleaned = open(file_cleaned)
    data_cleaned = np.fromfile(handle_file_cleaned,'f4')
    #Cleaned dataset
    total_seconds_cleaned = len(data_cleaned)*sampling_period #total seconds in dataset
    total_hours_cleaned =  total_seconds_cleaned / 3600 #total hours in dataset
    total_hours_rounded_cleaned = np.ceil(total_hours_cleaned) #total rounded hours in dataset
    
    log_handle.write(' \n ') 



    #%% Generate the TEMPO polycos for this observation
    
    #Create the custom TEMPO command for this file
    TEMPO_command = 'tempo -ZOBS=AR -ZFREQ=407.5 -ZTOBS='+str(total_hours_rounded_cleaned)+' -ZSTART='+str(start_time_GPS_astropy.mjd)+'  -ZNCOEFF=15 -ZSPAN='+str(int(total_hours_rounded_cleaned))+'H -f B0329+54.par'
    log_handle.write('TEMPO command: ' + TEMPO_command+'\n')
    #I round the start time to start a tiny bit earlier

    terminal_TEMPO_run = subprocess.run(TEMPO_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    log_handle.write(terminal_TEMPO_run.stdout.decode('utf-8')+'\n')
    
    
    #Here I add the name of the pulsar because for some reason, TEMPO does not put it in, and it is needed in PRESTO
    polyco_handle = open('polyco.dat','r+')
    polyco_contents = polyco_handle.read()
    polyco_handle.seek(0,0)
    polyco_handle.write('0332+5434  ')
    polyco_handle.close()
    
    #When doing TOA finding later, PRESTO looks for the polycos along with the fold
    copyfile('polyco.dat', path_to_folded_profiles+str(start_time_GPS)+'_PSR_0332+5434.pfd.polycos')
    
    log_handle.write(' \n ') 

    
    #%% Create PRESTO .inf file
    #This file contains information about the observation essential to the PRESTO folding software
    #Modify a template inf file. It has empty slots that need filled.
    
    copyfile('Template_PRESTO_inf_file.txt','current_PRESTO_inf_file.inf') #this creates an empty template file, and removes the previous instance of it
    
    #Write the datafile name, without suffix
    update_text(filename='current_PRESTO_inf_file.inf', lineno=1, column=44, text=file_cleaned[:-4])
    
    #Write the observation start MJD
    update_text(filename='current_PRESTO_inf_file.inf', lineno=8, column=44, text=str(start_time_GPS_astropy.mjd))
    
    #Write the number of bins in the time series
    update_text(filename='current_PRESTO_inf_file.inf', lineno=10, column=44, text=str(len(data_cleaned)))
    
    #PRESTO will look for this information file in the same location as the data file, with the same name
    copyfile('current_PRESTO_inf_file.inf', file_cleaned[:-3]+'inf')
    #PRESTO looks for an inf file along with the folded profiles later, when doing TOA finding
    copyfile('current_PRESTO_inf_file.inf', path_to_folded_profiles+str(start_time_GPS)+'.inf')
    #I currently get a warning saying that the .inf file cannot be found. I wonder why! It's OK, because the information taken from the inf file in that case defaults to the right values without one: DM 0 and number of channels 1.
    

    
    #%% Perform the fold for this observation
    
    
    
    PRESTO_fold_command = 'prepfold -nosearch '+absphase+' -polycos polyco.dat -psr 0332+5434 -double -noxwin -n '+number_of_profile_bins+' -o '+path_to_folded_profiles+str(start_time_GPS)+' '+file_cleaned
    
    #to try: window
    
    log_handle.write('PRESTO fold command: ' + PRESTO_fold_command+'\n')
    
    
    terminal_fold_run = subprocess.run(PRESTO_fold_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    log_handle.write(terminal_fold_run.stdout.decode('utf-8')+'\n')

    
    
    
    log_handle.write(' \n ')
    
    #%% Generate TOA and SNR for this observation
    
    path_to_template_profile = '/home/emma/Desktop/pulsardataprep_acreroad/Folding/Jodrell_Template_Profile_I-Q_PRESTO_Gaussian_fit.gaussians' #this was generated using PRESTO's pygaussfit.py on the Jodrell Bank template for this pulsar
    PRESTO_TOA_command = 'get_TOAs.py -f -n 1 -g '+path_to_template_profile+' '+path_to_folded_profiles+str(start_time_GPS)+'_PSR_0332+5434.pfd'
    

    
    log_handle.write('PRESTO TOA command: ' + PRESTO_TOA_command+'\n')
    log_handle.write('Output in PRESTO_TOAs.txt . \n')
    
    
    terminal_TOA_run = subprocess.run(PRESTO_TOA_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    PRESTO_TOAs_handle.write(terminal_TOA_run.stdout.decode('utf-8')+'\n')

    
    
    
    log_handle.write('\n \n \n \n \n')
    bar.next()
    

    
    
    
    
    
#%% Clean up
bar.finish()
print('\n')
print('\n')
print('Polycos, folding and retrieving TOAs took '+str(bar.elapsed)+' s. Now making total profile.')
os.remove('current_PRESTO_inf_file.inf')
os.remove('polyco.dat') #this was the predictor file of the last processed observation
PRESTO_TOAs_handle.close()

#%% Write the TOAs to a TEMPO-readable file

PRESTO_TOAs_handle = open('PRESTO_TOAs.txt' , 'r')
TEMPO_TOAs_handle = open('TEMPO_TOAs.txt', 'w')
FFTFIT_results_handle = open('FFTFIT_results.txt', 'w')

#to find floats, intergers, and numbers with exponents in output files, we need to use regular expressions
#this one was taken from https://stackoverflow.com/questions/4703390/how-to-extract-a-floating-number-from-a-string , second answer
regexp_numeric_pattern = r'[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
#this expression needs compiled by regexp
any_number = re.compile(regexp_numeric_pattern, re.VERBOSE)


for line in PRESTO_TOAs_handle:
    if 'SNR' in line:
        b, b_error, SNR, SNR_error, _, _, _  = any_number.findall(line) 
        FFTFIT_results_handle.write(b+' '+b_error+' '+SNR+' '+SNR_error+'\n')
    if 'a                407.500' in line:
        TEMPO_TOAs_handle.write(line)
TEMPO_TOAs_handle.close()
PRESTO_TOAs_handle.close()
FFTFIT_results_handle.close()

#%% Create a total profile

fold_files = glob.glob(path_to_folded_profiles+'/*.pfd')
folds_filenames_list_handle = open('folds_filenames_list.txt', 'w')
for fold_file in fold_files:
        folds_filenames_list_handle.write("%s\n" % fold_file)

PRESTO_totalprofile_command = 'sum_profiles.py -n '+number_of_profile_bins+' -g '+path_to_template_profile+' folds_filenames_list.txt'

log_handle.write('PRESTO total profile command: ' + PRESTO_totalprofile_command+'\n')

terminal_totalprofile_run = subprocess.Popen(PRESTO_totalprofile_command, stdin=subprocess.PIPE, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
time.sleep(3) #give it some time before pressing enter
output_totalprofile_run = terminal_totalprofile_run.communicate(input=b'\n \n \n \n')[0] #this program needs to have enter pressed twice
    
log_handle.write(output_totalprofile_run.decode('utf-8')+'\n')
total_profile = np.genfromtxt('sum_profiles.bestprof')


fig1 = plt.figure()
ax1 = plt.gca()
plt.step(total_profile[:,0],total_profile[:,1], linewidth=0.5, color='black')
ax1.set_xlabel('Pulse phase bins')
ax1.set_ylabel('Relative flux')
plt.savefig('Total_Profile.pdf') 
plt.close()

print('Finished.')


#%% Clean up
os.remove('folds_filenames_list.txt')

#%% Get some numbers out to compare with previous analyses' performance

FFTFIT_results = np.genfromtxt('FFTFIT_results.txt')
average_SNR = np.mean(FFTFIT_results[:,2])
log_handle.write('The average SNR is '+str(average_SNR))

for i in range(1,100):
    number_of_lines_from_end = str(i)
    line_bytes = subprocess.check_output(['tail', '-'+number_of_lines_from_end, 'PRESTO_Fold_All_Observations.log'])
    line = line_bytes.decode(encoding='utf-8')
    if 'Summed profile approx SNR' in line:
        total_profile_SNR = any_number.findall(line)
        break
log_handle.write('The summed profile\'s approximate SNR is '+total_profile_SNR[0])

TOA_list = np.genfromtxt('TEMPO_TOAs.txt')
average_TOA_error = np.mean(TOA_list[:,3])
log_handle.write('The average TOA error bar is '+str(average_TOA_error)+' microseconds.')


log_handle.close()




    
    
    
    
    
    
    
    
    

    
    



