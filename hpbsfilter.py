#Importing required libraries and scripts
import numpy as np
import matplotlib.pyplot as plt
import firfilter

#Global variables
#Loading the ecg data sampled at 1000Hz
ecg_data = np.loadtxt("ECG_1000Hz_13.dat")
fs = 1000
nofsamples = len(ecg_data)

#Plotting the frequency spectrum |H(k)| versus frequency of interest
def ecgFreqPlot(title,ecg_data,fs):
    ecgPlot = np.fft.fft(ecg_data)
    ecgPlot = abs(ecgPlot)
    freqAxis = np.linspace(0,fs,len(ecgPlot))
    plt.figure(figsize=(13.33,7.5))
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('|H(k)|')
    plt.title(title)
    plt.plot(freqAxis, ecgPlot)
    plt.show()

#Plotting the time domian of the signal of interest
def ecgNormPlot(title,data):
    fs = 1000
    time=np.linspace(0,len(data)/fs,len(data))
    plt.figure(figsize=(13.33,7.5))
    plt.xlabel('Time [s]')
    plt.ylabel('Amplitude [mV]')
    plt.title(title)
    plt.plot(time,data)
    plt.show()
    
#Function that employs dofilter() from the FIR_filter class to calculate the final samples
def finalfilteredECGData():
    FC = fir_coeff()
    filteredSamples = np.zeros(nofsamples)
    finalFSamples = np.zeros(nofsamples)
    
    #Filter coefficients to remove 50Hz DC noise wing a notch filter 
    Banstopcoeff = FC.bandstopDesign(1000, 45, 55)
    fir = firfilter.FIR_filter( Banstopcoeff )
    
    for x in range(nofsamples):
        filteredSamples[x] = fir.dofilter(ecg_data[x])
        
    #Filter coefficients to remove baseband wander till 0.7Hz    
    Highpasscoeff = FC.highpassDesign(1000, 0.7)
    fir = firfilter.FIR_filter( Highpasscoeff )
        
    for x in range(nofsamples):
        finalFSamples[x] = fir.dofilter(filteredSamples[x])
    return finalFSamples    

# FIR Filter coefficient class        
class fir_coeff():

    #Bandstop filter coefficient funcion that returns the bandstop coefficients
    def bandstopDesign(self,Fs,f1,f2):
        #Calculating the number of taps/ number of coefficients M with resolution of 0.7
        df = 0.07*abs(f1-f2)
        M = int(Fs/df)
        #Define the cutoff frequencies
        k1 = int(f1/Fs*M)
        k2 = int(f2/Fs*M)
        x=np.ones(M)
        x[k1:k2+1] = 0 
        x[M-k2: M-k1+1] = 0
        #Plotting the frequency response of the Bandstop filter
        # plt.figure(figsize=(13.33,7.5))
        # plt.xlabel("Frequency [Hz]")
        # plt.ylabel("X(k)")
        # plt.title("Ideal frequency response of Bandstop filter")
        # freqs= np.linspace(0,Fs,M)
        # plt.plot(freqs,x)
        x = np.fft.ifft(x)
        x = np.real(x)
        h = np.zeros(M)
        #Shifting the negatime time to positive time
        h[0:int(M/2)] = x[int(M/2):M]
        h[int(M/2):M] = x[0:int(M/2)]
        #Plotting the impulse response of the Bandstop filter
        # plt.figure(figsize=(13.33,7.5))
        # plt.xlabel("Coefficients/M")
        # plt.ylabel("h(n)")
        # plt.title("Impulse Response of bandstop filter")
        # naxis = np.linspace(0,M,M)
        #Applying the window function to smooth out the ripples
        h = h*np.hanning(M)
        # plt.plot(naxis,h)
        return h
    # Highpass coefficient funcion that returns the highpass coefficients
    def highpassDesign(self,Fs,fc):
        #Calculating the number of taps/ number of coefficients M
        f1=0;
        df = abs(f1-fc)
        M = int(Fs/df)
        #Define the cutoff frequency
        kc = int(fc/Fs*M)
        x=np.ones(M)
        x[0:kc+1] = 0 
        x[M-kc: ] = 0
        x = np.fft.ifft(x)
        x = np.real(x)
        h = np.zeros(M)
        #Shifting the negatime time to positive time
        h[0:int(M/2)] = x[int(M/2):M]
        h[int(M/2):M] = x[0:int(M/2)]
        #Applying the window function to smooth out the ripples
        h = h*np.hanning(M)
        return h
#Main of the hpbsilter program
if __name__ == "__main__":    
    


    #Calling the finalfilteredECGData function to return the final samples 
    F= finalfilteredECGData()   
    #Plotting the original response in time domain
    ecgNormPlot('Time domain response of the original ECG data',ecg_data)
    #Plotting the frequency response of time domain signal
    ecgFreqPlot('Frequency response of the ECG data',ecg_data, fs)
    #Plotting the filtered response in time domain
    ecgNormPlot('Time domain response of the filtered ECG data',F) 
    #Plotting the filtered frequency response in time domain      
    ecgFreqPlot('Frequency response of filtered ECG data',F, fs)
