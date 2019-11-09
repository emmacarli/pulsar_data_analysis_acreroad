# =============================================================================
# 
# This code finds all the raw and preprocessed files on ettus and plots their dates of recording.
# Author: Emma Carli emma.carli@outlook.com
# 
# =============================================================================
import pysftp

preproc_datafiles_list = []
raw_datafiles_list = []

with pysftp.Connection(host='ettus.astro.gla.ac.uk', username='astro') as sftp: #no password as I am on the .authorised_keys list
    print('Connection successfully established.')
    sftp.cwd('/home/astro/pulsartelescope/data')
    for file in sftp.listdir():
        if file.endswith('dd.dat'):
            raw_datafiles_list.append(file)
        if file.endswith('preproc.dat'):
            preproc_datafiles_list.append(file)
    
#there are much less raw than preprocessed files
#maybe try to get extra raw ones from these folders:
# =============================================================================
# ./home/astro/.local/share/Trash/files
# ./home/astro/GW/0329/data
# ./home/astro/GW/crab
# ./home/astro/pulsartelescope/data
# ./home/ronnie/mypulsartelescope/data/aug
# ./home/ronnie/mypulsartelescope/data/dec
# ./home/ronnie/mypulsartelescope/data/feb2015
# ./home/ronnie/mypulsartelescope/data/march2015
# ./home/ronnie/mypulsartelescope/data/oct
# ./home/ronnie/pulsartelescope/data
# =============================================================================

#then, plot the dates of recording for all these raw files, and for the preprocessed files too