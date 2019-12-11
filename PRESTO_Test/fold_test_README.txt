Trying out prepfold from PRESTO...

List of options: https://github.com/scottransom/presto/blob/e461225ab1df5ae93e6397081daf1b020f15495e/clig/prepfold_cmd.cli
Useful options:
Flag   -topo    topo    {Fold the data topocentrically (i.e. don't barycenter)}
Flag   -zerodm  zerodm  {Subtract the mean of all channels from each sample (i.e. remove zero DM)}
Flag   -absphase absphase  {Use the absolute phase associated with polycos}
Flag   -noclip  noclip  {Do not clip the data.  (The default is to _always_ clip!)}
Flag   -noxwin  noxwin  {Do not show the result plots on-screen, only make postscript files}
Flag   -nosearch nosearch {Show but do not search the p/pdot and/or DM phase spaces}
Flag   -scaleparts scaleparts {Scale the part profiles independently}
Flag   -justprofs justprofs {Only output the profile portions of the plot}
String -par parname {Name of a TEMPO par file from which to get PSR params}
String -polycos polycofile {File containing TEMPO polycos for psrname (not required)}

Rest infile {Input data file name.  If the data is not in a recognized raw data format, it should be a file containing a time series of single-precision floats or short ints.  In this case a '.inf' file with the same root filename must also exist (Note that this means that the input data file must have a suffix that starts with a period)}



What I did:
add observatory to obsys.dat in tempo (used the observatory long, lat, elev from Dr. Matt Pitkin's Presto trial) as such:
 3573761.379   -269164.277      5258393.2217   1  ACRE ROAD           -  AR

ran makeinf (see file - input some arbitrary values where I didn't know)
created B0329+54.par made from ATNF catalogue : https://www.atnf.csiro.au/research/pulsar/psrcat/proc_form.php?version=1.62&startUserDefined=true&c1_val=&c2_val=&c3_val=&c4_val=&sort_attr=jname&sort_order=asc&condition=&pulsar_names=B0329%2B54&ephemeris=short&submit_ephemeris=Get+Ephemeris&coords_unit=raj%2Fdecj&radius=&coords_1=&coords_2=&style=Long+with+last+digit+error&no_value=*&fsize=3&x_axis=&x_scale=linear&y_axis=&y_scale=linear&state=query


ran prepfold -noclip -nosearch -double -zerodm -noxwin -par B0329+54.par bestprofile_1185851408.100563_cleaned_2minsigmaclip.dat  
The polycos are produced but they seem to not take into account observatory location.

I abandoned the making of polycos directly with presto and I went to  use the prediction mode of tempo to make a polyco file. 
A tz.in file has to be made as well, which contains observatory, observing frequency and pulsar name.
Here are the tempo options I used:
  -z	        Compute polynomial coefficients for predictions 
  -f<par>       Over-rides the default parameter file name with <par>
I ran this command: tempo -z -f B0329+54.par and got a fortran error:
At line 46 of file tzinit.f
Fortran runtime error: End of file

Error termination. Backtrace:
#0  0x7faf11ae42da in ???
#1  0x7faf11ae4ec5 in ???
#2  0x7faf11ae568d in ???
#3  0x7faf11c5ba33 in ???
#4  0x7faf11c549c4 in ???
#5  0x7faf11c560f9 in ???
#6  0x55a8fe9d5948 in tzinit_
	at /home/emma/PULSAR_SOFTWARES/tempo/src/tzinit.f:46
#7  0x55a8fe9ce7e7 in tempo
	at /home/emma/PULSAR_SOFTWARES/tempo/src/tempo.f:286
#8  0x55a8fe98bcfe in main
	at /home/emma/PULSAR_SOFTWARES/tempo/src/tempo.f:511



Trying to use  -Z<par>=<val> New method for specifying polynomial coefficient calculations
                Any -Z parameter invokes this mode and minimizes tempo output
                -Z parameters
                Parameter: Default:      Description:
                PSR                      Pulsar name (same as PULSAR)
                PULSAR                   Pulsar name (same as PSR)
                OBS                      Observatory (same as SITE)
                SITE                     Observatory (same as OBS)
                OUT        polyco.dat    Output file name
                START      current time  Start time for polyco block
                NCOEFF     15            Number of coefficients
                FREQ       1420          Radio frequency of observation
                SPAN       60            Time span in seconds for polyco block
                                           (xxxH or xxxM for hours or minutes)
                TOBS       1             Observing time in hours
                                           (xxxM or xxxS for minutes or seconds)

just returned usage. It would be good to be able to input start time and observing time.
TBC...





