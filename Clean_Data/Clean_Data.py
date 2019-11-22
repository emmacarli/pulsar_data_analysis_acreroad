# =============================================================================
# 
# This code cleans all raw pulsar data files and plots a comparison of the two versions. 
# Author: Emma Carli emma.carli@outlook.com
#
# =============================================================================


#%% Clear variables

from IPython import get_ipython
get_ipython().magic('reset -f') 

#%% Import packages

import matplotlib.pyplot as plt
from scipy import signal

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

#%% Remove running median
signal.medfilt2d()

