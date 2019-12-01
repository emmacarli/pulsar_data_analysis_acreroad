# =============================================================================
# Mirror, mirror, on the wall, who is the best profile of them all?
# Find profile with highest SNR within Graham's, to try out my folding on.
# Author: Emma Carli
# emma.carli@outlook.com
# =============================================================================

# =============================================================================
# 
# IN THIS CODE THE TIME FORMAT HAS BEEN SET BUT NOT THE SCALE/TIME STANDARD. THIS IS NOT PRECISE.
# 
# =============================================================================

#%% Clear variables

from IPython import get_ipython
get_ipython().magic('reset -f') 

#%% Import packages
import numpy as np
from astropy.time import Time

#%% Read in Graham's TOAs
TOAs_Graham = np.genfromtxt('Original_TOAs_by_Graham.txt', skip_header=1, usecols=(2,3), dtype=float) #columns 2 and 3 in the TEMPO .tim FORMAT 1 file is the MJD and its error 

#%% Find the MJD of the first TOA for which I have a raw file

minimum_GPS_time = Time(1178454286.107926, format='gps') #this is the first date at which I start having raw files. 
for MJD_row, MJD in enumerate(TOAs_Graham[:,0]): #go through each Julian Date TOA, they are in increasing order
    if MJD > minimum_GPS_time.mjd:
        minimum_MJD = MJD
        minimum_MJD_row = MJD_row
        break
    
#%% Find the strongest profile, i.e. the best dataset
        
max_SNR_MJD = TOAs_Graham[np.argmin(TOAs_Graham[minimum_MJD_row:,1])+minimum_MJD_row,0] #find the Julian Date at which the error was the minimum, i.e. the folded profile has the maximum SNR of all, within available raw files
max_SNR_MJD_astropy = Time(max_SNR_MJD, format='mjd')
max_SNR_GPS = Time(max_SNR_MJD_astropy, format='gps')

#%%

print('The profile with the highest SNR was folded from the datafile which recording started on approximately'+str(max_SNR_GPS.value)+' GPS time.')
