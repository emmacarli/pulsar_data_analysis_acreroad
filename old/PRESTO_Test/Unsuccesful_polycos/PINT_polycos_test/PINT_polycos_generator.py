# =============================================================================
#
# Generate polycos using PINT for folding with PRESTO.
# Author: Emma Carli
#
# =============================================================================



#%% Clear variables
from IPython import get_ipython
get_ipython().magic('reset -f') 


#%% Import packages
from pint import polycos, observatory, models
import astropy
import sys

#%% Start a log
log_handle = open('PINT_polycos_generator.log', 'w')

sys.stdout = log_handle
sys.stderr = log_handle


#%% Observatory definition 
acre_latitude = 55.902528 #from clicking on pulsar telescope at acre road in Google Maps
acre_longitude = -4.307107 #from clicking on pulsar telescope at acre road in Google Maps
acre_height = 50 #meters
acre_EarthLocation = astropy.coordinates.EarthLocation.from_geodetic(lon=acre_longitude, lat=acre_latitude, height=acre_height)
acre_itrs = acre_EarthLocation.get_itrs() #wonder if itrs and itrf is the same thing...


observatory.topo_obs.TopoObs('acre', aliases=['AR', 'acreroad'], itrf_xyz = acre_itrs.data.xyz )

#Normally, an observatory only has to be defined once. 
#A list of observatories created in the past can be found under pint/observatory/observatories.py
#It didn't seem to save for me, so I entered it manually.

#%%Generate model
B032954_model = models.model_builder.get_model('B0329+54.par')
#this parameter file's data was obtained from ATNF

#%% Generate polycos
pl = polycos.Polycos() #initiate an empty polycos instance
pl.generate_polycos(model = B032954_model, mjdStart = 57969.1, mjdEnd = 57969.4, obs = 'acre', segLength = 5, ncoeff = 12, obsFreq = 407.5, method = 'TEMPO') #segment length in minutes, observing frequency in MHz, method TEMPO2 unavailable

#%% Write to TEMPO style polyco table (PRESTO uses these for folding)
pl.write_polyco_file(format='tempo', filename='PINT_polycos.dat')

