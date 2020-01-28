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

#%% Plot data

fig1 = plt.figure()
ax1 = plt.gca()
ax1.plot(phase_bins, Jodrell_template[:,1], label='I', linewidth=0.7)
ax1.plot(phase_bins, Jodrell_template[:,2], label='Q', linewidth=0.7)
ax1.plot(phase_bins, Jodrell_template[:,1]-Jodrell_template[:,2], label='I-Q', linewidth=0.7) #We are observing <E_y^2>, if <E_x^2> need I+Q
ax1.set_xlim(0.4,0.6)
ax1.set_xlabel('Pulse phase')
ax1.set_ylabel('Flux density (Wm$^{-2}$Hz$^{-1}$)')
ax1.legend()
plt.savefig('Jodrell_Template_Profile.pdf') 
plt.close()

#%% Save data
Jodrell_Template_Profile_IminusQ = np.c_[phase_bins, Jodrell_template[:,1]-Jodrell_template[:,2]]
np.savetxt('Jodrell_Template_Profile_I-Q.txt', Jodrell_Template_Profile_IminusQ )




