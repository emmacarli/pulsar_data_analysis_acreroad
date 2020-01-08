Author: Emma Carli 
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
add observatory to obsys.dat in tempo (used the observatory long, lat, elev from ettus' obsys.dat) as such:
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

tempo -Z PSR=B0329+54 OBS=AR FREQ=407.5 TOBS=4.1 START=57969.13183339089 -f B0329+54.par 


just returned usage. It would be good to be able to input start time and observing time.
if can't fix this, could try PINT instead.
TBC...


My confusion was that error thrown out by presto is same as tempo
While presto problem seems to be unsolvable and related to having anaconda only: https://github.com/scottransom/presto/issues/73 
But tempo isn't using python!
Graham suggests the following explanation : "Fortran compile error is because it's compiling from source. When you install Tempo it will install the source code and then compiles it with GCC, which has option flags for Fortran. Some version of something won't be compatible with this compiling. Could be anaconda with Presto and something else with Tempo."


Workaround of the problem: I try generating polycos from ettus using Tempo2, which is good because Tempo2 is a more precise, scientifically accurate computation.

In tempo2, you can make polycos in the format of tempo with the option -polyco "mjd1 mjd2 nspan ncoeff maxha site_code freq"
From tempo2 manual:
"This will request that tempo2 makes a prediction for a parameter file from MJDs mjd1 to mjd2 with each divided
into segments each of nspan minutes. The number of coefficients for use in the fitting, ncoeff.
The maximum hour angle range for the prediction, maxha. The observatory site for the prediction
is site code at an observing frequency of freq.(note the use of the quote marks around the parameters). Tempo2 should produce a file
(polyco new.dat) that takes the form of tempo1.
Tempo2 also produces a file (newpolyco.dat) which has the same parameters, but listed to more
decimal places. Each parameter is listed on an individual line.
note: the tempo1 software switches off clock corrections in predictive mode. To emulate
this the CLK flag in the parameter file should be set to CLK UNCORR."

So I ran: tempo2 -f B0329+54.par -polyco "57969.1 57969.4 40 12 8 acre 407.5" -tempo1
Note: acre is the tempo2 keyword in ettus -- observatory codes work by keyword in tempo2.
I chose 40 mins for nspan minutes as I was getting a "tspan too short" error before. 
I get errors: "no clock corrections available for clock UTC(acre) for MJD 57969.1", "MJD is outside of UT1 table range  (MJD 57969.1)". So the ephemeris available stops before 2017? Need to update it. or maybe try with integer dates.


I'm gonna try using PINT instead because it's so much more user-friendly, modern etc.















