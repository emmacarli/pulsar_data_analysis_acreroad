#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 23 17:16:19 2020

@author: emma
"""
from pint import models, toa , residuals, fitter
import matplotlib.pyplot as plt
from astropy import units
from astropy.visualization import quantity_support


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
ax3.vlines(56769, -100000, 100000, linewidth=0.5, color='red', label='Jumps')
ax3.vlines(56794, -100000, 100000, linewidth=0.5, color='red')
ax3.vlines(57048, -100000, 100000, linewidth=0.5, color='red')
ax3.vlines(57575, -100000, 100000, linewidth=0.5, color='red')
ax3.set_title("%s Pre-fit Timing Residuals" % model.PSR.value)
ax3.set_xlabel("MJD")
ax3.set_ylabel("Residual ($\mu$s)")
plt.legend()
#plt.savefig('Pre_fit_residuals.pdf') 
#plt.close()


# Perform the fit
WLS_fit = fitter.WLSFitter(TOAs, model)
WLS_fit.set_fitparams('F0','F1', 'RAJ', 'DECJ') 
WLS_fit.fit_toas()

fig4 = plt.figure()
ax4 = plt.gca()

# Plot the post-fit residuals
ax4.errorbar(TOAs.get_mjds().value, WLS_fit.resids.time_resids.to(units.us), yerr=TOAs.get_errors().to(units.us), color='black', elinewidth=0.05, capsize=0, marker='o',markersize=0.8, linestyle='none')
#ax4.scatter(TOAs.get_mjds().value, WLS_fit.resids.time_resids.to(units.us), marker='.', color='black')
ax4.set_title("%s Post-Fit Timing Residuals" % model.PSR.value)
ax4.set_xlabel("MJD")
ax4.set_ylabel("Residual ($\mu$s)")
plt.savefig('Post_fit_residuals.pdf')
plt.savefig('Post_fit_residuals_no_error_bars.pdf') 
plt.close()


