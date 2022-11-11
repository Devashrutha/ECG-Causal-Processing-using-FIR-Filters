#Importing required libraries
import numpy as np

#Defining the FIR_filter class
class FIR_filter:
    #Defing the constructor that initialises the class variables
    def __init__( self, _coefficients ):
        self.coeffFIRFilter = _coefficients
        self.nofTaps = len(_coefficients)
        self.ringbuffer = np.zeros(self.nofTaps)
        self.ringBuffOffset = 0
        self.buffer = np.zeros(self.nofTaps)
    
    def dofilter( self, inpVal ):
        # Store the new value at current offset 
        self.ringbuffer[self.ringBuffOffset] = inpVal
        
        # Set offset variables
        offset = self.ringBuffOffset
        coeffOffset = 0
        
        # Initialize the output to zero
        output = 0
        
        # Multiply ecg data values with coefficients until it reaches the beginning of the ring buffer
        while( offset >= 0 ):
            # Calculate M/ tap value and add it to the output
            output += self.ringbuffer[offset] * self.coeffFIRFilter[coeffOffset] 
            # Move offsets 
            offset -= 1
            coeffOffset += 1
    
        # Set the offset to the end of the array 
        offset = self.nofTaps - 1
        
        # Multiply the coefficients until it reaches the start of the ring buffer
        while( self.ringBuffOffset < offset ):
            # Calculate tap value and add it to a sum
            output += self.ringbuffer[offset] * self.coeffFIRFilter[coeffOffset] 
            # Move the offsets 
            offset -= 1
            coeffOffset += 1
           
        # Check if the next inpVal would be placed beyond the size of the ring buffer and prevent it 
        if( (offset + 1) >= self.nofTaps ):
            self.ringBuffOffset = 0
        # Otherwiise the next offset value does not  exceed the ring buffer index limit
        else:
            self.ringBuffOffset += 1
            
        return output
    
    #Function to clear the ring buffer for next set of coefficients
    def ResetFilter( self ):
        # Reset the current offset and clear the ringbuffer 
        self.ringBuffOffset = 0
        self.ringbuffer = np.zeros(self.nofTaps)
        
    #Function that creats a linear buffer for LMS causal processing    
    def causalLms(self,inpVal):
        for j in range(self.nofTaps-1):
            self.buffer[self.nofTaps-j-1] = self.buffer[self.nofTaps-j-2]
        self.buffer[0] = inpVal
        return np.inner(self.buffer,self.coeffFIRFilter)
    
    #Funcion that computes the coefficients for LMS Filter
    def doFilterAdaptive(self,error,learningRate):
        for i in range(self.nofTaps):
            self.coeffFIRFilter[i] = self.coeffFIRFilter[i]+error*learningRate*self.buffer[i]
            