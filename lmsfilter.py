#Importing required libraries and scripts
import numpy as np
import firfilter
import hpbsfilter

#Global variables
fs = 1000
M = fs

#Smaller learning rate is better for the filter ro settle faster initially
learningrate = 0.001

#Define the frequency of the sinusodial noise injection
noiseFreq = 50
ecg_data = np.loadtxt("ECG_1000Hz_13.dat")

#Initialise the FIR_filter coefficients
filterdata = firfilter.FIR_filter(np.zeros(M))

#Calculate the filter coefficients with the delta coefficients added due to feedback
z = np.empty(len(ecg_data))
for i in range(len(ecg_data)):
    referenceNoise = np.sin(2*np.pi*noiseFreq/fs*i)
    summerOutputVar = filterdata.causalLms(referenceNoise)
    output = ecg_data[i]-summerOutputVar
    filterdata.doFilterAdaptive(output, learningrate)
    z[i]= output

#Plotting the original ECG data in time domain
hpbsfilter.ecgNormPlot("Time domain response of the original ECG data", ecg_data)
#Plotting the filtered ECG data in time domain
hpbsfilter.ecgNormPlot("Time domain response of the LMS filtered ECG data", z)
#Plotting the original ECG data in frequency domain
hpbsfilter.ecgFreqPlot("Frequency response of the original ECG data", ecg_data, fs)
#Plotting the filterd ECG data in frequency domain
hpbsfilter.ecgFreqPlot("Frequency response of the LMS filtered ECG data", z, fs)