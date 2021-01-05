# pulsar_data_analysis_acreroad

## Radio data analysis pipeline for the pulsar telescope at Acre Road Observatory, Glasgow, Scotland. Cleans up raw observations of PSR J0332+5434, then folds them in topocentric phase, retrieves a TOA and SNR per four hour observation, performs pulsar timing and generates a total profile added in phase with an updated timing model.

For more information refer to pdf report.

To run this iPython notebook, you need a Linux system with PRESTO, PINT and TEMPO installed. I have included notes on how to install them at the end of this README.

You also need an installation of all the Python packages imported at the beginning of the notebook.

The notebook requires the following files in the working directory:
- Template_PRESTO_inf_file.txt (created with PRESTO's makeinf, has several fields left empty)
- J0332+5434_initial_parameters.par, that contains the parameters in table 1 and 2 of the report
- Jodrell_Template_Profile_I-Q.txt (see report, and Template_Generator folder)
- Jodrell_Template_Profile_I-Q_PRESTO_Gaussian_fit.gaussians (made with PRESTO's pygaussfit.py on the template above)


Change the paths at the beginning of the notebook to the location of the raw files from the Acre Road pulsar telescope. Set where the files cited above are located, as well as where you want your results saved.

Add the Acre Road observatory to TEMPO's obsys.dat, and make sure no other observatories have the codes 'a' and 'AR':

	3573741.1      -269156.74      5258407.3      1  ACRE                a  AR 

Add the observatory to PRESTO, in get_TOAs.py, near the start, there is a dictionary of telescopes for TEMPO called scopes={...}. Add to the list: 

	,'AR':'a'} 
	
just after 

	'Geocenter':'o' 

Add the observatory to PINT, in observatory/observatories.py

	TopoObs('acre', aliases=['acreroad','a','AR'], itrf_xyz =[3573741.1, -269156.74, 5258407.3], )


## Notes on how to install TEMPO and PRESTO:

Sources:

- https://blog.csdn.net/sinat_34850075/article/details/52434526

- https://github.com/scottransom/presto/blob/master/INSTALL

- https://docs.google.com/document/d/1v8Dm4f-SOeDQX5Yli6syek1pxtqgpw81b1cxqoqv2aU

- http://zhaozhen.me/2017/10/16/ubuntu-software-presto.html

- http://tempo.sourceforge.net/

- https://summerpulsar.wordpress.com/2015/01/12/more-presto-installation/




To install PRESTO and TEMPO please refer to https://emmacarli.github.io/2020/04/02/PRESTO-and-TEMPO-installation . PINT has clear instructions in their docs.


## Useful links:
- PINT documentation: https://nanograv-pint.readthedocs.io/en/latest/
- Pulsar profile template: http://www.epta.eu.org/epndb/#gl98/J0332+5434/gl98_408.epn
- TEMPO documentation: http://tempo.sourceforge.net/reference_manual.html
- Really nice literature review (and many other pulsar things!): http://alex88ridolfi.altervista.org/pagine/pulsar_literature.html
- ATNF catalogue parameters for J0332+5434: https://www.atnf.csiro.au/research/pulsar/psrcat/proc_form.php?version=1.62&JName=JName&RaJ=RaJ&DecJ=DecJ&PMRA=PMRA&PMDec=PMDec&PX=PX&PosEpoch=PosEpoch&F0=F0&F1=F1&PEpoch=PEpoch&Age=Age&Bsurf=Bsurf&startUserDefined=true&c1_val=&c2_val=&c3_val=&c4_val=&sort_attr=jname&sort_order=asc&condition=&pulsar_names=j0332\%2B5434&ephemeris=selected&submit_ephemeris=Get+Ephemeris&coords_unit=raj\%2Fdecj&radius=&coords_1=&coords_2=&style=Long+with+last+digit+error&no_value=*&fsize=3&x_axis=&x_scale=linear&y_axis=&y_scale=linear&state=query


	

