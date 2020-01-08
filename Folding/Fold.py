# =============================================================================
# 
# This code folds a 4-hour observation. 
# Author: Emma Carli
#
# =============================================================================


#%% Clear variables

from IPython import get_ipython
get_ipython().magic('reset -f') 

#%% Import packages

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

#%% Set known variables


#%% Go through each observation

#for each cleaned dataset:

    #%% Make TEMPO2 polycos -- probably the most precise ones.
    
    #convert GPS start time with astropy into ??? for tempo2
    #make sure to set the correct time standard

    #compute end time for tempo2
    
    #run command line tempo2 command 
    
    #upload predictor file for this observation
    
    #%% Create an array of phases, and divide the data into time bins
    
    #%% Fold
    
    #for each time bin in the dataset:
  
        #interpolate frequency from predictor file
        
        #calculate phase of a time bin using formula in report
        
        #calculate standard deviation of data in a time bin
        
        #input into right array entry, weighted by standard deviation (1/std^2)

