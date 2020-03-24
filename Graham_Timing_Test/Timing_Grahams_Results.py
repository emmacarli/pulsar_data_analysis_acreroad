from pint import models, toa , residuals, fitter
import matplotlib.pyplot as plt
from astropy import units
from astropy.visualization import quantity_support
import numpy as np

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


# Import model
model = models.model_builder.get_model('J0332+5434_Grahams_initial_parameters.par')

# Import TOAs
TOAs = toa.get_TOAs('J0332+5434_Grahams_Observations.tim', planets=True)

# Compute pre-fit residuals
prefit_residuals = residuals.Residuals(TOAs, model)

# Plot them, with the jumps
fig3 = plt.figure()
ax3 = plt.gca()
ax3.errorbar(
    TOAs.get_mjds().value,
    prefit_residuals.time_resids.to(units.us),
    yerr=TOAs.get_errors().to(units.us),
    marker='o',markersize=0.5,
    color='black', elinewidth=0.5, capsize=0, linestyle='none')
ax3.vlines(56769, np.min(prefit_residuals.time_resids.to(units.us)),  np.max(prefit_residuals.time_resids.to(units.us)), linewidth=0.5, color='red', label='Jumps')
ax3.vlines(56794, np.min(prefit_residuals.time_resids.to(units.us)),  np.max(prefit_residuals.time_resids.to(units.us)),  linewidth=0.5, color='red')
ax3.vlines(57048, np.min(prefit_residuals.time_resids.to(units.us)),  np.max(prefit_residuals.time_resids.to(units.us)), linewidth=0.5, color='red')
ax3.vlines(57575, np.min(prefit_residuals.time_resids.to(units.us)),  np.max(prefit_residuals.time_resids.to(units.us)),  linewidth=0.5, color='red')
ax3.set_title("%s Pre-fit Timing Residuals" % model.PSR.value)
ax3.set_xlabel("MJD")
ax3.set_ylabel("Residual ($\mu$s)")
plt.legend()
plt.savefig('Pre_fit_residuals.pdf') 
plt.close()


# Perform the fit
WLS_fit = fitter.WLSFitter(TOAs, model)
WLS_fit.set_fitparams('F0','F1', 'RAJ', 'DECJ')
WLS_fit.fit_toas()

fig4 = plt.figure()
ax4 = plt.gca()

# Plot the post-fit residuals
ax4.errorbar(TOAs.get_mjds().value, WLS_fit.resids.time_resids.to(units.us), yerr=TOAs.get_errors().to(units.us), color='black', elinewidth=0.05, capsize=0, marker='o',markersize=0.8, linestyle='none')
ax4.vlines(56769,  np.min(WLS_fit.resids.time_resids.to(units.us)),  np.max(WLS_fit.resids.time_resids.to(units.us)), linewidth=0.5, color='red', label='Jumps')
ax4.vlines(56794, np.min(WLS_fit.resids.time_resids.to(units.us)),  np.max(WLS_fit.resids.time_resids.to(units.us)), linewidth=0.5, color='red')
ax4.vlines(57048, np.min(WLS_fit.resids.time_resids.to(units.us)),  np.max(WLS_fit.resids.time_resids.to(units.us)), linewidth=0.5, color='red')
ax4.vlines(57575, np.min(WLS_fit.resids.time_resids.to(units.us)),  np.max(WLS_fit.resids.time_resids.to(units.us)), linewidth=0.5, color='red')
ax4.set_title("%s Post-Fit Timing Residuals" % model.PSR.value)
ax4.set_xlabel("MJD")
ax4.set_ylabel("Residual ($\mu$s)")
plt.legend()
plt.savefig('Post_fit_residuals.pdf')
plt.close()
