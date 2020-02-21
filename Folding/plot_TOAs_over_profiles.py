
import numpy as np
import matplotlib.pyplot as plt
import glob
from astropy.time import Time, TimeDelta
from astropy import units

path_to_folded_profiles =  '/home/emma/Desktop/pulsardataprep_acreroad/Folding/PRESTO_Folded_Profiles/'




folded_profiles_paths = sorted(glob.glob(path_to_folded_profiles+'/*.pfd.bestprof'))
TOA_list = np.genfromtxt('TEMPO_TOAs.txt')

for profile_number, folded_profile_path in enumerate(folded_profiles_paths): 
    folded_profile = np.genfromtxt(folded_profile_path, skip_header=26 )
    
    start_time_GPS = float(folded_profile_path[len(path_to_folded_profiles):-len('_PSR_0332+5434.pfd.bestprof')])
    start_time_GPS_astropy = Time(start_time_GPS, format='gps') 

    TOA = TOA_list[profile_number-1, 2]
    TOA_error = TOA_list[profile_number-1, 3]
    TOA_astropy = Time(TOA, format='mjd')
    TOA_error_astropy = TimeDelta(TOA_error * units.us)
    
    
    TOA_from_start_of_observation = TOA_astropy - start_time_GPS_astropy
    
    fig0 = plt.figure()
    ax0 = plt.gca()
    ax0.step(folded_profile[:,0],folded_profile[:,1], linewidth=0.5, color='black')
    ax0.vlines(TOA_from_start_of_observation.to('s'), ymax = np.max(folded_profile[:,1]), colors='r', linestyles='dashed', label='TOA' )
    #ax0.hlines()

    ax0.set_xlabel('Pulse phase bins')
    ax0.set_ylabel('Relative flux')
    
    plt.savefig(path_to_folded_profiles+'Folded_Profile'+str(start_time_GPS)+'.pdf') 
    plt.close()


