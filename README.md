# pulsardataprep_acreroad

Radio data analysis software for the pulsar telescope at Acre Road Observatory, Glasgow, Scotland.

To run this notebook, you need PRESTO and TEMPO installed. I have included notes on how to install them at the end of this README.

You also need an installation of all the packages imported at the beginning of the notebook.





You also need the following files:
- Template_PRESTO_inf_file.txt (created with PRESTO's makeinf)
- J0332+5434_initial_parameters.par, that contains the parameters in table 1 and 2 of the report
- Jodrell_Template_Profile_I-Q.txt (see other scripts)
- Jodrell_Template_Profile_I-Q_PRESTO_Gaussian_fit.gaussians (made with PRESTO's pygaussfit.py and the I-Q template from the EPN database - see report and other scripts)


Change the paths at the beginning of the notebook.
Add the Acre Road observatory to TEMPO's obsys.dat, and make sure no other observatories have the codes 'a' and 'AR':
 3573741.1      -269156.74      5258407.3      1  ACRE                a  AR 
Add the observatory to PRESTO, in get_TOAs.py, near the start, there is a dictionary of telescopes for TEMPO called scopes={...}. Add to the list: ,'AR':'a'} just after 'Geocenter':'o' .
Add the observatory to PINT, in observatory/observatories.py
TopoObs('acre', aliases=['acreroad','a','AR'], itrf_xyz =[3573741.1, -269156.74, 5258407.3], )




Notes on how to install TEMPO and PRESTO:

Sources:
https://blog.csdn.net/sinat_34850075/article/details/52434526
https://github.com/scottransom/presto/blob/master/INSTALL
https://docs.google.com/document/d/1v8Dm4f-SOeDQX5Yli6syek1pxtqgpw81b1cxqoqv2aU
http://zhaozhen.me/2017/10/16/ubuntu-software-presto.html
http://tempo.sourceforge.net/
https://summerpulsar.wordpress.com/2015/01/12/more-presto-installation/



What I've run on my Ubuntu 18.04 64 bit to install PRESTO, for use in _Python_:

	sudo apt-get update

	cd ~
	mkdir PULSAR_SOFTWARE

	sudo apt-get install git libfftw3-bin libfftw3-dbg libfftw3-dev libfftw3-doc libfftw3-double3 libfftw3-long3 libfftw3-quad3 libfftw3-single3 pgplot5 csh automake gfortran libglib2.0-dev libccfits-dev libcfitsio5 libcfitsio-dev libx11-dev libpng-dev 

	cd PULSAR_SOFTWARE/
	git clone http://git.code.sf.net/p/tempo/tempo

	cd tempo
	./prepare
	./configure
	make && sudo make install
	cp tempo.cfg src/
	cp tempo.hlp src/
	cd ..

	git clone http://github.com/scottransom/presto.git

	sudo gedit /etc/environment

added to the end of my PATH:
	:/home/emma/PULSAR_SOFTWARES/presto/bin"

then added:
	TEMPO="/home/emma/PULSAR_SOFTWARES/tempo/src"

	PRESTO="/home/emma/PULSAR_SOFTWARES/presto"

	PGPLOT_DIR="/usr/lib/pgplot5"

	FFTW_PATH="/usr"

	LD_LIBRARY_PATH="/home/emma/PULSAR_SOFTWARES/presto/lib"


	git clone https://github.com/scottransom/pyslalib.git
	cd pyslalib
	python setup.py install


	cd /home/emma/PULSAR_SOFTWARE/presto/src

	make makewisdom
	make prep
	make
	make clean

	cd $PRESTO ; pip install .

	cd lib
	sudo cp libpresto.so /usr/lib



Some Python commands will not work because PRESTO is not entirely compatible with Anaconda installations: https://github.com/scottransom/presto/issues/73 . The ones needed for this project (pygaussfit.py, prepfold, sum_profiles.py, get_TOAs.py) work.



