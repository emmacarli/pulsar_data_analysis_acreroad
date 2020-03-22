# =============================================================================
#
# Plot the Jodrell Bank template Stokes parameters.
# Save the Stokes parameters corresponding to our observations to file.
# Author: Emma Carli
#
# =============================================================================



#%% Clear variables
from IPython import get_ipython
get_ipython().magic('reset -f') 


#%% Import packages
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats

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

#%% Import data from Jodrell Bank (all parameters are in this file)
#from http://www.epta.eu.org/epndb/#gl98/J0332+5434/gl98_408.epn
Jodrell_template = np.genfromtxt('gl98_408.txt')
#The first column of the Jodrell template is the pulse phase in seconds. It ends at a full period of the pulsar.
phase_bins = Jodrell_template[:,0]/0.714519699726 #divide by pulsar rotation period from ATNF

#%% Save data
Jodrell_Template_Profile_IminusQ = np.c_[phase_bins, Jodrell_template[:,1]-Jodrell_template[:,2]]
np.savetxt('Jodrell_Template_Profile_I-Q.txt', Jodrell_Template_Profile_IminusQ )

#%% Once pygaussfit.py is ran on the data and the result saved, we can plot the result on top of it 
const = 109.27180 
phas1 = 0.46200 
fwhm1 = 0.00801 
ampl1 = 69.34160 
phas2 = 0.52655 
fwhm2 = 0.00934
ampl2 = 126.17658 
phas3 = 0.49828 
fwhm3 = 0.00940 
ampl3 = 1254.58176 

fig1 = plt.figure()
ax1 = plt.gca()
fitted_profile = (ampl1*scipy.stats.norm.pdf(phase_bins, phas1, fwhm1/2.35482))+(ampl2*scipy.stats.norm.pdf(phase_bins, phas2, fwhm2/2.35482))+(ampl3*scipy.stats.norm.pdf(phase_bins, phas3, fwhm3/2.35482))+const

ax1.step(phase_bins, fitted_profile , label='PRESTO 3-Gaussian \n approximation of I-Q', color='blue')
plt.fill_between(phase_bins,fitted_profile, step="pre", alpha=0.3, linewidth=1.5, color='blue')



#%% Plot data


ax1.step(phase_bins, Jodrell_template[:,1], label='I', linewidth=0.7, color='black')
ax1.step(phase_bins, Jodrell_template[:,2], label='Q', linewidth=0.7, color='black', linestyle='--')
ax1.step(phase_bins, Jodrell_template[:,1]-Jodrell_template[:,2], label='I-Q', linewidth=1.5, color='red') #We are observing <E_y^2>, if <E_x^2> need I+Q
plt.fill_between(phase_bins,Jodrell_template[:,1]-Jodrell_template[:,2], step="pre", alpha=0.3, color='red')
ax1.set_xlim(0.45,0.54)
ax1.set_xlabel('Pulse phase')
ax1.set_ylabel('Flux density (Wm$^{-2}$Hz$^{-1}$)')
ax1.legend(loc='best')
plt.savefig('Jodrell_Template_Profile.pdf') 
plt.close()

#%%



