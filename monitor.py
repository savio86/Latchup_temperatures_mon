import sys
import serial
from multiprocessing import Queue
import datetime
import serial.tools.list_ports
import numpy as np

from lib_monitor import *
#-------------------------------------------------------------------------------------------------------------------
def temperature_request():										# put in the queue the request to read the temperatures				
	q.put(b"t")

#-------------------------------------------------------------------------------------------------------------------
def current_request():										# put in the queue the request to read the temperatures				
	q.put(b"c")

#-------------------------------------------------------------------------------------------------------------------

port = serial.tools.list_ports.comports()[0]
print(port.description)

q = Queue()												#define a queue for multi-thread messaging
out_file = setupLogFile() # runId is incremented inside this function
try:
	ser = serial.Serial('COM5')  		#select the serial port
	ser.baudrate = 9600 										#set baudrate to 9600bps
	
																
	if not ser.isOpen():										#check if the port is not already open
		ser.open() 												#open serial port
		
	if  ser.isOpen():
		com_num = ser.portstr
		print ("Serial port " + com_num + " opened"+"\n")
		writeLogFile(out_file, "Serial port " + str(com_num) + " opened")
	else:														#if the port is still closed, exit
		print('Error: impossible to open the serial port'+"\n")
		writeLogFile(out_file, 'Error: impossible to open the serial port')
		sys.exit()
	
	
	t = perpetualTimer(1, temperature_request)					#start the thread that each N seconds asks to the main thread
	t.start() 													#to send a request to the MCU

	c = perpetualTimer(10, current_request)					#start the thread that each N seconds asks to the main thread
	c.start() 													#to send a request to the MCU

	while 1:													#main loop
		
		if not q.empty():										#if there is a request to the MCU in queue
			q_get = q.get()
			buffer = serial_request (ser, q_get)				#send the command to the MCU and read back the result
			if b'!' in buffer:									#check if meanwhile a letch-up occurred
				latchup=handle_latchup(ser)						#if yes, handle it and throw away the other information
				writeLogFile(out_file, "Latch-up!!")
				print ("Latch-up!! "+str(latchup)+"\n")			#the first string is referred to the 1.8V and the second to 3.3V
				writeLogFile(out_file, str(latchup))
			else:
				if q_get == b't':
					values = separate_string( buffer )				#if there wasn't , separate the string in a list of values 
					temperatures = np.array(get_temp_values (values))			#convert the string in the value
					print ("t:", temperatures.round(2))
					writeLogFile(out_file, "t: "+str(temperatures.round(2)))
					writeLogFile(out_file, "t r: "+str(values)) # adding raw values
				elif q_get == b'c':
					values = separate_string( buffer )				#if there wasn't , separate the string in a list of values 
					current = np.array(get_current_value (values))			#convert the string in the value
					print ("c", current.round(1))
					writeLogFile(out_file, "c: "+str(current.round(1)))
					writeLogFile(out_file, "c r: "+str(values)) # adding raw values
		byteincoming = ser.inWaiting()							
		if byteincoming != 0:									#if a byte is incoming w/o any request is a Latch-up event
			buffer = ser.read(byteincoming)						#read the serial buffer
			if '!' in buffer:									#check if it is a latch-up 
				latchup = handle_latchup(ser)					#if yes, handle it
				writeLogFile(out_file, "Latch-up!!")
				print ("Latch-up!! "+str(latchup)+"\n")          #the first string is referred to the 1.8V and the second to 3.3V
				writeLogFile(out_file, str(latchup) )
except (KeyboardInterrupt, SystemExit):							#on ctrl + C signal
		t.cancel()												#close the thread
		c.cancel()												#close the thread
		
		ser.close ()											#close the serial port and exit
		print ("Serial port " + ser.portstr + " closed"+"\n")
		writeLogFile(out_file,  "Serial port " + str(ser.portstr) + " closed")
		sys.exit()






