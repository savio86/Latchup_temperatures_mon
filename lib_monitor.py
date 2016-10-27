from threading import Timer,Thread,Event
import time
#-------------------------------------------------------------------------------------------------------------------
class perpetualTimer():											#this class define an infinite thread with a timer
																#each N second call a function

   def __init__(self,t,hFunction):
      self.t=t
      self.hFunction = hFunction
      self.thread = Timer(self.t,self.handle_function)

   def handle_function(self):
      self.hFunction()
      self.thread = Timer(self.t,self.handle_function)
      self.thread.start()

   def start(self):
      self.thread.start()

   def cancel(self):
      self.thread.cancel()

#-------------------------------------------------------------------------------------------------------------------	  
def serial_request ( serial, byte_to_send ):							#send a char to the MCU and read back the answer
	serial.write( byte_to_send )									#write on serial port
	data_from_serial = 0
	byteincoming = 0
	time.sleep( 1 )												#wait
	while byteincoming == 0:
		byteincoming = serial.inWaiting()
	data_from_serial = serial.read(byteincoming)
	return (data_from_serial)									#return a string

#-------------------------------------------------------------------------------------------------------------------	
def separate_string ( input_string ):							# split the string in a list of string
	value_list = input_string.split(b' ')
	return(value_list)
#-------------------------------------------------------------------------------------------------------------------
def get_temp_values( ADC_read_list ):							#convert the list of string into the list of the temperatures
	values_array=[]
	for i in range(len(ADC_read_list)):
		if ADC_read_list[i] !=b'#':								#check and skip the last char 
			temp = ((2558.66 * ((float(ADC_read_list[i])*5)/1024) )/(5- ((float(ADC_read_list[i])*5)/1024)))-255.866
			rounded_temp= round(temp,3)
			values_array.append(rounded_temp)
	return (values_array)										#return the list of float
#-------------------------------------------------------------------------------------------------------------------	
	
def get_pressure_value( ADC_read ):								#convert the string into the pressure value
	value = (float(ADC_read)/9.21) + 10.56
	return(value)												#return a float
#-------------------------------------------------------------------------------------------------------------------
def handle_latchup(serial):										#handle a latch-up event
	buffer = serial_request (serial, b'l')						#request the total amount of latch-up
	if b'!' in buffer:
		buffer = buffer.replace(b"!", b"")
	latchup = [int(item) for item in buffer.split(b' ')]
	return (latchup)