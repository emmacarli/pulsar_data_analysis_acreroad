import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

template_profile = np.genfromtxt('/home/emma/Desktop/pulsardataprep_acreroad/PRESTO_Test/TOA_find_test/Jodrell_Template_Profile_I-Q.txt')
template_profile =  template_profile[:,1]/np.max(template_profile)
total_profile = np.genfromtxt('/home/emma/Desktop/pulsardataprep_acreroad/Folding/sum_profiles.bestprof')
total_profile =  total_profile[:,1]
total_profile = np.roll(total_profile, np.argmax(total_profile))
total_profile =  signal.resample(total_profile, len(template_profile))
total_profile =  total_profile/np.max(total_profile)

plt.step(range(443), total_profile, linewidth=0.5, color='black', label='Total Profile')
plt.step(range(443), template_profile, linewidth=0.5, color='red', label='Template Profile')
