#Importing required libraries
import numpy as np
from matplotlib import pyplot as plt
import firfilter
import hpbsfilter

#Function that plots the time domain waveform of the signal of interest
def PlotWaveform(title, ycords):
    fs=1000
    plt.figure(figsize=(13.33,7.5))
    plt.title(title)
    plt.xlabel('Time [s]') 
    plt.ylabel('Amplitude [mV]')
    time=np.linspace(0,len(ycords)/fs,len(ycords))
    plt.plot(time,ycords)  
    plt.show()

#Function that plots the step graph for of the Momentary Heart Rate    
def PlotWaveformStep(title, ycords):
    fs=1000
    plt.figure(figsize=(13.33,7.5))
    plt.title(title)
    plt.xlabel('Time [s]') 
    plt.ylabel('Amplitude [mV]')
    time=np.linspace(0,len(ycords)/fs,len(ycords))
    plt.step(time,ycords)  
    plt.show()

#Function that creates the ecg template for the matched FIR filter 
def GenerateECGTemplate(samples, samplingFrequency):
    filteredSamples = []
    finalSamples = []
    # Create the filter coefficients to remove the 50Hz noise and baseband wander
    bandstopfir = hpbsfilter.fir_coeff()
    firCoefficients = bandstopfir.bandstopDesign(1000, 45, 55)
    
    # Initialize FIR 
    fir = firfilter.FIR_filter(firCoefficients)
    
    # Generating the tempelate from only the first 4000 samples to prevent long wait time
    for x in range(4000):
        filteredSamples.append(fir.dofilter(samples[x]))
    
    highpassfir = hpbsfilter.fir_coeff()
    firCoefficients = highpassfir.highpassDesign(1000, 0.5)
    
    # Initialize FIR 
    fir = firfilter.FIR_filter(firCoefficients)
    

    for x in range(4000):
        finalSamples.append(fir.dofilter(filteredSamples[x])) 
           
    # Plot Filtered ECG waveform
    PlotWaveform("Filtered ECG", finalSamples)
        
    # Get one Period of ECG to form the template
    ecgSlice = finalSamples[2800:3600] # [760:870]
    # Flip to create the time reversed tempelate for the filter coefficients 
    template = np.flip(ecgSlice)
    
    # Plotting both the ECG slices 
    hpbsfilter.ecgNormPlot('ECG Slice', ecgSlice)
    hpbsfilter.ecgNormPlot('ECG Template', template)
    
    # Reset FIR filters ringbuffer and offset
    fir.ResetFilter()
    
    # Return the filter object and template coefficients 
    return fir, template

#Main body of the program
if __name__ == "__main__":
    #Load the ecg data
    ecg_data = np.loadtxt("ECG_1000Hz_13.dat")
    fs = 1000
    nofsamples = len(ecg_data)
    fir, template = GenerateECGTemplate(ecg_data, 1000) 
    filteredSmaples = np.zeros(nofsamples)
    squaredSamples = np.zeros(nofsamples)
    
    # Peak Detector with Heart rate tracking
    #Define the peak detector variables
    peakIndex = []
    # Momentary heart rate array
    m = []
    lastPeak = 0
    nPeaks = 0
    
    #Heuristics variable to prevent bogus detection
    pulseSettlingSamplecCnt = 37 
    peakFlag = False 
    
    #Set the threshold to detect peaks based on the amplitude of the delta plulses
    amplitudeThreshold = 20
    
    # Initialize matched filter object
    Templatefir = firfilter.FIR_filter(template)

    # Simulate causal system by filtering signal sample by sample
    # Filter the baseband wander and 50hH
    filteredSmaples = hpbsfilter.finalfilteredECGData()
    for x in range(nofsamples):
    
        # Apply the matched filter to generate the peaks 
        squaredSamples[x] = Templatefir.dofilter(filteredSmaples[x])
        # Square the output samples to pronounce the amplitude and suppress the noise to get the delta pulses
        squaredSamples[x] = squaredSamples[x] * squaredSamples[x]
        
        # Wait for the filter to settle
        if(x > 2000):
            
            # Detect the peaks 
            # If sample amplitude is above threshold, the peak hasn't been detected yet with some heuristics to prevent bogus detections
            if( squaredSamples[x] > amplitudeThreshold and peakFlag == False and (x - lastPeak ) >= pulseSettlingSamplecCnt ):
                
                peakFlag = True
                
            # If the amplitude exceeded the threshold and previous sample was higher that must've been a peak
            if( squaredSamples[x - 1] > squaredSamples[x] and peakFlag == True ):
                
                peakFlag = False 
                
                # Holding the index as last peak index 
                lastPeak = (x - 1)
                #Append the index of that sample to list
                peakIndex.append( lastPeak )
                # Increment peak counter
                nPeaks += 1 
                
                # Calculating the momentary heart rate in BPM
                #Minimum of 2 peaks are required to generate the number of samples between them
                if ( nPeaks >= 2):
                    # Calculating the number of samples between peaks
                    t = lastPeak - peakIndex[ nPeaks - 2]
                    # Calculating the momentary rate in BPM
                    m.append( (fs/t)*60 )
     
    

    # Plotting the original time domain response of the ECG
    hpbsfilter.ecgNormPlot('Time domain signal of the original ECG', ecg_data) 
    # Plotting the filtered time domain response of the ECG
    hpbsfilter.ecgNormPlot('Time domain signal of the filtered ECG', filteredSmaples)  
    # Plotting the filtered frequency response of the ECG 
    hpbsfilter.ecgFreqPlot('Frequency responce of the filtered ECG',filteredSmaples,fs)     
    #Plotting the delta pulses returned by the matched filter
    PlotWaveform("Delta Pulses obtained after matched filtering", squaredSamples) 
    #Plotting the momentary heart rate as a step graph
    PlotWaveformStep("Momenrary Heart Rate", m)       
    #Print the number of heart beats detected
    print("Number of beats detected: " + str(nPeaks) )
    #Print the average BMP detected from the delta pulses
    print("Average Momentary Heart Rate (in BPM): %.1f" % (sum(m)/len(m)))
 