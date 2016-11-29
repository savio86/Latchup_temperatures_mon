from threading import Timer,Thread,Event
import time
import os, datetime

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
def setupLogFile(logdir = './data'):
	# open empty log file, return file name
	# retrive last runId, add 1, use it for this run and write to file
	runIdfile = open("runId.cfg", "r")
	runId = int(runIdfile.readlines()[0]) + 1
	print("Begin of run %d" % runId)
	runIdfile = open("runId.cfg", "w+")
	runIdfile.write("%s" % runId)
	
	# build file name Id and string
	current_id = "%06d_%s" %(runId, str(datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S')))
	file_name = os.path.join(logdir, current_id+"_log.txt")	
	out_file = open(file_name, 'w')
	out_file.write("# Begin of run %d %s \n" %(runId, current_id))
	out_file.close()
	return(file_name)
	
def writeLogFile(file_name, file_str):
	# open file in append mode, write a line and close it
	out_file = open(file_name, 'a')
	out_file.write(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))+"\t" + file_str +"\n")
	out_file.close()
	return(None)
	
	
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
	for ADC_read in ADC_read_list:
		if ADC_read !=b'#':								#check and skip the last char 
			try:
				temp = (1./3.9083E-3)*( 1.*(float(ADC_read)/1023)/(1.- (float(ADC_read)/1023)) - 1.)
			except ZeroDivisionError:
				temp = 9999.
			values_array.append(temp)
	return (values_array)										#return the list of float
#-------------------------------------------------------------------------------------------------------------------	
	
def get_pressure_value( ADC_read ):								#convert the string into the pressure value
	value = (float(ADC_read)/9.21) + 10.56
	return(value)												#return a float

#-------------------------------------------------------------------------------------------------------------------	
def get_current_value( ADC_read):						#convert the string into the current value
	# list of 3.3V, 1.8V current in adc values,
	# return current in mA, gain calibrated by hand
	return ([0.09108*float(ADC_read[0]), 0.9108*float(ADC_read[1])])
	
#-------------------------------------------------------------------------------------------------------------------
def handle_latchup(serial):										#handle a latch-up event
	buffer = serial_request (serial, b'l')						#request the total amount of latch-up
	if b'!' in buffer:
		buffer = buffer.replace(b"!", b"")
	latchup = [int(item) for item in buffer.split(b' ')]
	return (latchup)