#!/usr/bin/env python
# coding: utf-8

# MSci thesis by 2185343, 2020 - see report for details.
# 
# This is a summary version of all the code written for this project. Some scripts are left out for clarity, notably the FFT transform section, plotting scripts, Gaussian fitting of the template, and repeated steps. The whole project is available on GitHub (under my name).

# ## General parameters

# In[ ]:


# For interactive plots, use:
#%matplotlib ipympl

# Import packages
import numpy as np
import matplotlib.pyplot as plt
from progress.bar import Bar #https://pypi.org/project/progress/

from astropy.stats import sigma_clip
from astropy.time import Time
from astropy import units
from astropy.visualization import quantity_support


from pint import models, toa, residuals, fitter
from scipy.signal import resample


from My_Functions.update_text import update_text #taken from https://stackoverflow.com/questions/49742962/how-to-insert-text-at-line-and-column-position-in-a-file
from shutil import copyfile
import os, re, time, subprocess, glob


# Make text larger for readability on graphs
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['font.size'] = 14
# Set same fonts as my LaTeX document
plt.rcParams['font.family'] = 'STIXGeneral' 
plt.rcParams['mathtext.fontset'] = 'stix'
# Other plotting params
plt.rcParams['axes.grid'] = True
plt.rcParams["figure.figsize"] = [10,10]


# In[ ]:


# Set known variables from observations

sampling_period = 2e-3 #2 milliseconds
one_second_in_datapoints = int(1/sampling_period) #500 datapoints = 1 second of recording
one_minute_in_datapoints= one_second_in_datapoints * 60


# In[ ]:


# Set paths

path_to_raw_files = '/home/emma/Desktop/Raw_Datafiles/'
path_to_cleaned_files = '/home/emma/Desktop/Cleaned_Data/'
path_to_folded_profiles =  '/home/emma/Desktop/pulsardataprep_acreroad/Folding/PRESTO_Folded_Profiles/'
path_to_template_profile = '/home/emma/Desktop/pulsardataprep_acreroad/Folding/Jodrell_Template_Profile_I-Q_PRESTO_Gaussian_fit.gaussians' #this was generated using PRESTO's pygaussfit.py on the Jodrell Bank template for this pulsar


# Files needed in the working directory: Template_PRESTO_inf_file.txt , 

# ## Data cleaning

# In[ ]:


# Make a list of raw files' paths in my computer
raw_files = glob.glob(path_to_raw_files+'*-PSRB0329-2ms-sampling-dd.dat') #this suffix is added at recording

bar = Bar('Processing...', max=len(raw_files), fill='\U0001F4E1', suffix = '%(percent).1f%% - %(eta)ds') #create a progress bar
bar.check_tty = False

# Go through each raw file
for raw_file in raw_files: 
    start_time_GPS = float(raw_file[len(path_to_raw_files):-len('-PSRB0329-2ms-sampling-dd.dat')]) #the start of the filename gives the beginning of the recording time in GPS format
    bar.next()
      
    #If this file has already been cleaned, skip it and go to the next in raw_files
    if glob.glob(path_to_cleaned_files+str(start_time_GPS)+'_cleaned.dat') != []:
        print(str(start_time_GPS)+' already cleaned.')
        continue
    
    # Load in the raw data
    handle_raw_file = open(raw_file, mode='rb') 
    data_raw = np.fromfile(handle_raw_file,'f4')
    
    # Crop the raw file to a length that is an integer number of minutes
    # so that can perform operations over one minute / one second intervals
    number_of_one_minute_intervals = int( np.floor( len(data_raw) / one_minute_in_datapoints ))
    data1 = data_raw[0: number_of_one_minute_intervals * one_minute_in_datapoints] #step 1 of cleaning
    
    # Remove median of whole dataset
    data2 = data1 - np.median(data1) #step 2 of cleaning
    
    # Median removal over 1 second intervals (not a proper filter with sliding window!)
    median_filter_1s = np.zeros(len(data2))
    number_of_one_second_intervals = number_of_one_minute_intervals * 60

    second_long_chunks_starting_points = np.linspace(0, len(data2) - one_second_in_datapoints , number_of_one_second_intervals , dtype='int')

    for second_long_chunk_start in second_long_chunks_starting_points :
        second_long_chunk_end =  second_long_chunk_start + one_second_in_datapoints
        
        median_filter_1s[second_long_chunk_start : second_long_chunk_end] = np.median(data2[second_long_chunk_start : second_long_chunk_end]) 

    data3 = data2 - median_filter_1s #step 3 of cleaning

    # Sigma clip over 1 minute intervals
    data4 = np.zeros(len(data3))
    
    minute_long_chunks_starting_points = np.linspace(0, len(data3) - one_minute_in_datapoints , number_of_one_minute_intervals , dtype='int')
    
    for minute_long_chunk_start in minute_long_chunks_starting_points :
        minute_long_chunk_end =  minute_long_chunk_start + one_minute_in_datapoints
        
        sigma_masked_array = sigma_clip(data3[minute_long_chunk_start : minute_long_chunk_end], sigma=5, cenfunc='median', masked=True) #this is a NumPy MaskedArray object
        sigma_masked_array.set_fill_value(0.0)
        
        data4[minute_long_chunk_start : minute_long_chunk_end] = sigma_masked_array.filled()
        
    # STD divide to whiten data over a 1 minute interval
        data_cleaned = np.zeros(len(data4))
        
        for minute_long_chunk_start in minute_long_chunks_starting_points :
    
            minute_long_chunk_end =  minute_long_chunk_start + one_minute_in_datapoints
            
            if np.std(data4[minute_long_chunk_start : minute_long_chunk_end]) != 0 :
                data_cleaned[minute_long_chunk_start : minute_long_chunk_end] = data4[minute_long_chunk_start : minute_long_chunk_end]/np.std(data4[minute_long_chunk_start : minute_long_chunk_end]) #4th and last step of cleaning
        
    # Write the cleaned file in the same way as a raw file, so can be opened the same way
    handle_file_cleaned = open(path_to_cleaned_files+str(start_time_GPS)+'_cleaned.dat', 'wb')
    data_cleaned_binary = np.array(data_cleaned, 'f4')
    data_cleaned_binary.tofile(handle_file_cleaned)
    
    # Close files
    handle_file_cleaned.close()
    handle_raw_file.close()


bar.finish()


# ## Folding, SNR and TOA computations

# #### General parameters

# In[ ]:


# This is the number of phase bins in the folded profiles and in the total profile, it has to be a power of two, for FFTFIT.
# Otherwise, for folding, PRESTO defaults to the number of sampling bins which correspond to one folded period, in our case about 64, and for the total profile, it defaults to 128.
number_of_profile_bins = '512' #I chose this amount to limit computation time and 

# Start a log
log_handle = open('PRESTO_Fold_SNR_TOA.log', 'w')


# Find out time span of the available observations (for information and context only)

# In[ ]:


cleaned_files_paths = sorted(glob.glob(path_to_cleaned_files +'*_cleaned.dat'))
minimum_GPS_time = Time(float(cleaned_files_paths[0][len(path_to_cleaned_files):-len('_cleaned.dat')]), format='gps', scale='utc') #this is the first date at which I start having observations, extracted from the first file name of the ordered cleaned files.
log_handle.write('The observations start on ' + minimum_GPS_time.iso+'\n')
maximum_GPS_time = Time(float(cleaned_files_paths[len(cleaned_files_paths)-1][len(path_to_cleaned_files):-len('_cleaned.dat')]), format='gps', scale='utc') #this is the last observation date
log_handle.write('The observations end on ' + maximum_GPS_time.iso+'\n')
observations_span = maximum_GPS_time - minimum_GPS_time
log_handle.write('The observations span '+str(observations_span.jd)+' days. \n')
log_handle.write('\n \n \n \n') 


# In[ ]:


PRESTO_TOA_SNR_handle = open('PRESTO_TOAs_SNRs.txt' , 'w') #create a new file for saving PRESTO's TOA and SNR output


# #### Pulsar topocentric frequency predictions, folding, SNR and TOA computations

# In[ ]:


bar = Bar('Processing...', max=len(cleaned_files_paths), fill='\U0001F4E1', suffix = '%(percent).1f%% - %(eta)ds') #create a progress bar
bar.check_tty = False

for cleaned_file_path in cleaned_files_paths:
    
    # Find out the start time and length of the observation
    
    start_time_GPS = float(cleaned_file_path[len(path_to_cleaned_files):-len('_cleaned.dat')])
    start_time_GPS_astropy = Time(start_time_GPS, format='gps', precision=6, scale='utc') #important step! 
    log_handle.write('Observation starting on GPS time '+str(start_time_GPS)+' i.e. '+str(start_time_GPS_astropy.iso)+'\n')
    handle_cleaned_file = open(cleaned_file_path)
    data_cleaned = np.fromfile(handle_cleaned_file,'f4') #cleaned dataset
    total_seconds_cleaned = len(data_cleaned)*sampling_period #total seconds in dataset
    total_hours_cleaned =  total_seconds_cleaned / 3600 #total hours in dataset
    total_hours_rounded_cleaned = np.ceil(total_hours_cleaned) #total rounded hours in dataset
    
    log_handle.write(' \n ') 

    


    # Generate the TEMPO polynomial coefficients for this observation
    
    # Create the custom TEMPO command for this file
    TEMPO_command = 'tempo -ZOBS=AR -ZFREQ=407.5 -ZTOBS='+str(total_hours_rounded_cleaned)+' -ZSTART='+str(start_time_GPS_astropy.mjd)+'  -ZNCOEFF=15 -ZSPAN='+str(int(total_hours_rounded_cleaned))+'H -f J0332+5434_initial_parameters.par'
    log_handle.write('TEMPO command: ' + TEMPO_command+'\n')

    terminal_TEMPO_run = subprocess.run(TEMPO_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    log_handle.write(terminal_TEMPO_run.stdout.decode('utf-8')+'\n') #copy the TEMPO output to the log
    
    # Here I add the name of the pulsar because for some reason, TEMPO does not put it in, and it is needed in PRESTO
    polyco_handle = open('polyco.dat','r+')
    polyco_contents = polyco_handle.read()
    polyco_handle.seek(0,0)
    polyco_handle.write('0332+5434  ')
    polyco_handle.close()
    
    # When doing TOA finding later in this for loop, PRESTO looks for the polycos along with the folded profile
    copyfile('polyco.dat', path_to_folded_profiles+str(start_time_GPS)+'_PSR_0332+5434.pfd.polycos')
    
    log_handle.write(' \n ') 
    
    
   

    # Create PRESTO .inf file for this observation
    # This file contains information about the observation essential to the PRESTO folding software
    # Modify a template inf file. It has empty slots that need filled.
    
    copyfile('Template_PRESTO_inf_file.txt', 'current_PRESTO_inf_file.inf') #this creates an empty template file, and overwrites the previous instance of it
    
    # Write the datafile name, without suffix
    update_text(filename='current_PRESTO_inf_file.inf', lineno=1, column=44, text=cleaned_file_path[:-len('.dat')])
    
    # Write the observation start MJD
    update_text(filename='current_PRESTO_inf_file.inf', lineno=8, column=44, text=str(start_time_GPS_astropy.mjd))
    
    # Write the number of bins in the time series
    update_text(filename='current_PRESTO_inf_file.inf', lineno=10, column=44, text=str(len(data_cleaned)))
    
    # PRESTO will look for this information file in the same location as the data file, with the same name. This will overwrite any previous instances.
    copyfile('current_PRESTO_inf_file.inf', cleaned_file_path[:-len('dat')]+'inf')
    # PRESTO also looks for an inf file along with the folded profiles later, when doing TOA finding
    copyfile('current_PRESTO_inf_file.inf', path_to_folded_profiles+str(start_time_GPS)+'_cleaned.inf')

    
    
    
    # Perform the fold for this observation
    
    PRESTO_fold_command = 'prepfold -nosearch -absphase -polycos polyco.dat -psr 0332+5434 -double -noxwin -n '+number_of_profile_bins+' -o '+path_to_folded_profiles+str(start_time_GPS)+' '+cleaned_file_path)
    log_handle.write('PRESTO fold command: ' + PRESTO_fold_command+'\n')
    
    terminal_fold_run = subprocess.run(PRESTO_fold_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    log_handle.write(terminal_fold_run.stdout.decode('utf-8')+'\n')
    
    log_handle.write(' \n ')
    
    
    
    
    # Compute TOA, TOA error and SNR using FFTFIT
    PRESTO_TOA_SNR_command = 'get_TOAs.py -f -n 1 -g '+path_to_template_profile+' '+path_to_folded_profiles+str(start_time_GPS)+'_PSR_0332+5434.pfd'
    
    log_handle.write('PRESTO TOA command: ' + PRESTO_TOA_SNR_command+'\n')
    log_handle.write('Output in PRESTO_TOAs.txt . \n')
    
    terminal_TOA_SNR_run = subprocess.run(PRESTO_TOA_SNR_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    
    PRESTO_TOA_SNR_handle.write(terminal_TOA_SNR_run.stdout.decode('utf-8')+'\n')
    #I currently get a warning saying that the .inf file cannot be found. I wonder why! It's OK, because the information taken from the inf file in the case of TOA finding defaults to the right values: DM 0 and number of channels 1.
    
    
    
    
    log_handle.write('\n \n \n \n \n')
    bar.next()


# Post-loop cleanup

# In[ ]:


bar.finish()
time.sleep(2)
print('Polycos, folding and retrieving TOAs took '+str(bar.elapsed-2)+' s.')
os.remove('current_PRESTO_inf_file.inf') #inf file of the last processed observation
os.remove('polyco.dat') #this was the predictor file of the last processed observation
PRESTO_TOA_SNR_handle.close() #close the file, as it was open for writing and now we want to read it


# #### Extract the SNR and TOAs (with error) from the PRESTO output and save them into separate files

# In[ ]:


PRESTO_TOA_SNR_handle = open('PRESTO_TOAs_SNRs.txt' , 'r')
TOAs_handle = open('TOAs_TEMPO_format.txt', 'w') #the TOAs are saved as output by PRESTO, i.e. in a TEMPO format
FFTFIT_results_handle = open('FFTFIT_results.txt', 'w')

#to find floats, integers, and numbers with exponents in output files, we need to use regular expressions
#this one was taken from https://stackoverflow.com/questions/4703390/how-to-extract-a-floating-number-from-a-string , second answer
regexp_numeric_pattern = r'[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
#this expression needs compiled by regexp
any_number = re.compile(regexp_numeric_pattern, re.VERBOSE)


for line in PRESTO_TOA_SNR_handle:
    if 'SNR' in line:
        b, b_error, SNR, SNR_error, _, _, _  = any_number.findall(line) 
        FFTFIT_results_handle.write(b+' '+b_error+' '+SNR+' '+SNR_error+'\n')
    if 'a                407.500' in line: #a is the TEMPO one-letter code from obsys.dat
        TOAs_handle.write(line)
        
        
TOA_list = np.genfromtxt('TOAs_TEMPO_format.txt')
FFTFIT_results = np.genfromtxt('FFTFIT_results.txt')
FFTFIT_results_with_MJDs = np.zeros((len(TOA_list[:,2]),np.size(FFTFIT_results,1)+1))
FFTFIT_results_with_MJDs[0,:] = TOA_list
FFTFIT_results_with_MJDs[:,1:np.size(FFTFIT_results,1)+2]= FFTFIT_results
np.savetxt('FFTFIT_results.txt', FFTFIT_results_with_MJDs, format='%f')
#GETS SAVED REALLY WEIRDLY WITH LOADS OF EXTRA DIGITS...?
PRESTO_TOA_SNR_handle.close()
FFTFIT_results_handle.close()


# #### Plot SNR and TOA results 

# In[ ]:


SNR_list = FFTFIT_results[:,2]
average_SNR = np.mean(SNR_list)
log_handle.write('The average SNR is '+str(average_SNR)+'\n')

average_TOA_error = np.mean(TOA_list[:,3])
log_handle.write('The average TOA error bar is '+str(average_TOA_error)+' microseconds.\n')

fig1 = plt.figure()
ax1 = plt.gca()
ax1.scatter(TOA_list[:,2], SNR_list, marker='o', markersize = 1, color='black')
ax1.set_xlabel('TOA (MJD)')
ax1.set_ylabel('SNR')
plt.savefig('SNR_vs_TOA.pdf') 
plt.close()

fig2 = plt.figure()
ax2 = plt.gca()
ax2.scatter(SNRs, TOA_list[:,3],  marker='o', color='black')
ax2.set_xlabel('SNR')
ax2.set_ylabel('TOA error bar ($\mu$s)')
plt.savefig('TOA_errors_vs_SNRs.pdf') 
plt.close()


# In[ ]:


log_handle.close()


# # Pulsar timing fit

# #### Import data

# In[ ]:


# Add the first observed TOA to the model as a reference for zero phase (with error)
# This is a standard procedure
# TZRMJD = Zero Timing Residual MJD
model_with_TZRMJD_handle = open('J0332+5434_initial_parameters_with_TZRMJD.par') #this will erase any previous instance
model_with_TZRMJD_handle.write('TZRMJD		'+str(TOA_list[0,2])+'   '+str(TOA_list[0,3]))
# Copy the model 
for line in open('J0332+5434_initial_parameters') :
    model_with_TZRMJD_handle.write(line)


# Import model
model = models.model_builder.get_model('J0332+5434_initial_parameters.par')

# Import TOAs
TOAs = toa.get_TOAs('TOAs_TEMPO_format.txt', planets=True)

# Apply SNR cutoff
SNR_cutoff = 4
SNR_list_masked = np.ma.masked_where(SNR_list<SNR_cutoff, SNR_list)
TOAs.select(~SNR_list_masked.mask)
TOAs.print_summary()


# #### Pre-fit residuals

# In[ ]:


prefit_residuals = residuals.Residuals(TOAs, model)

# Plot them
fig3 = plt.figure()
ax3 = plt.gca()
ax3.errorbar(
    TOAs.get_mjds().value,
    prefit_residuals.time_resids.to(units.us),
    yerr=TOAs.get_errors().to(units.us),
    fmt=".", color='black', elinewidth=0.5, capsize=0)
ax3.set_title("%s Pre-fit Timing Residuals" % model.PSR.value)
ax3.set_xlabel("MJD")
ax3.set_ylabel("Residual ($\mu$s)")
plt.savefig('Pre_fit_residuals.pdf') 
plt.close()


# #### Fitting and post-fit residuals

# In[ ]:


# Perform the fit
WLS_fit = fitter.WLSFitter(TOAs, model)
WLS_fit.set_fitparams('F0','F1', 'RAJ', 'DECJ') 
WLS_fit.fit_toas()

fig4 = plt.figure()
ax4 = plt.gca()

# Plot the post-fit residuals
ax4.errorbar(TOAs.get_mjds().value, WLS_fit.resids.time_resids.to(units.us), yerr=TOAs.get_errors().to(units.us), fmt='.', color='black', elinewidth=0.5, capsize=0)
#ax4.scatter(TOAs.get_mjds().value, WLS_fit.resids.time_resids.to(units.us), marker='.', color='black')
ax4.set_title("%s Post-Fit Timing Residuals" % model.PSR.value)
ax4.set_xlabel("MJD")
ax4.set_ylabel("Residual ($\mu$s)")
plt.savefig('Post_fit_residuals.pdf')
#plt.savefig('Post_fit_residuals_no_error_bars.pdf') 
plt.close()

# Write the updated timing model 
model_handle = open('J0332+5434_post-fit_parameters.par', 'w')
model_handle.write(WLS_fit.model.as_parfile())
model_handle.close()


# # Total summed profile 

# In[ ]:


# Before this is done, you must run the folding, SNR and TOA computations with the updated model, in absolute phase. To do so, add '-absphase' to the PRESTO command.


# In[ ]:


# Import the template profile
template_profile = np.genfromtxt(path_to_template_profile)
phase_bins = template_profile[:,0]
template_profile =  template_profile[:,1]/np.max(template_profile)


# List the profiles to add, in chronological order
profile_files_paths = np.array(sorted(glob.glob(path_to_folded_profiles+'*.bestprof')))


SNR_cutoffs = np.linspace(1,7,25) #create a range of SNR cutoffs which will select profiles to be added in the total profile
mean_residuals = []
max_residuals = []

for SNR_cutoff in SNR_cutoffs:
    
    total_profile = np.zeros(512)

    for profile_file_path, SNR in zip(profile_files_paths[SNR_list>SNR_cutoff] , SNR_list[SNR_list>SNR_cutoff]):
        profile = np.genfromtxt(profile_file_path, skip_header=26)[:,1]
        
        total_profile += profile*SNR
        
    # Convert the total profile to a format compatible with the template    
    total_profile = np.roll(total_profile, int(len(total_profile)/2))
    total_profile -= np.median(total_profile)
    total_profile =  resample(total_profile, len(template_profile))
    total_profile =  total_profile/np.max(total_profile)
    
    residuals = template_profile - total_profile
    mean_residuals.append(np.mean(residuals))
    max_residuals.append(np.max(residuals))
    

# =============================================================================
#     fig1 = plt.figure()
#     ax1=plt.gca()
#     plt.step(phase_bins, total_profile, linewidth=0.5, color='black', label='Total Profile')
#     plt.step(phase_bins, template_profile, linewidth=0.5, color='red', label='Template Profile')
#     plt.legend()
#     ax1.set_title('Total profile comparison SNR cutoff '+str(SNR_cutoff))
#     ax1.set_xlabel("Phase")
#     ax1.set_ylabel("Relative intensity")
#     plt.savefig('Total_Profile_Comparison_SNR_cutoff_'+str(SNR_cutoff)+'.pdf') 
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

#Now choose the best cutoff.
#With this new cutoff you can repeat the PINT timing and update your model.
#Then you can perform this total profile again, with the chosen cutoff.

