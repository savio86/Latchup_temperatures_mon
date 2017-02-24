import sys
import serial
from multiprocessing import Queue
import datetime, time
import serial.tools.list_ports
import numpy as np
#import winsound
SoundFreq = 3000
SoundDuration= 300

from lib_monitor import *
#-------------------------------------------------------------------------------------------------------------------
def temperature_request():										# put in the queue the request to read the temperatures				
	q.put(b"t")

#-------------------------------------------------------------------------------------------------------------------
def current_request():										# put in the queue the request to read the temperatures				
	q.put(b"c")

#-------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------
def pressure_request():										# put in the queue the request to read the temperatures				
	q.put(b"p")

#-------------------------------------------------------------------------------------------------------------------

port = serial.tools.list_ports.comports()[0]
print(port.description)

RECOVERY_TIME = 1. # time for recovery after a latchup, written in Arduino firmware

q = Queue()												#define a queue for multi-thread messaging
out_file = setupLogFile() # runId is incremented inside this function
start_time = time.time() # time in seconds
try:
	ser = serial.Serial('/dev/ttyACM0')  		#select the serial port
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
	
	
	t = perpetualTimer(10, temperature_request)					#start the thread that each N seconds asks to the main thread
	t.start() 													#to send a request to the MCU

#	c = perpetualTimer(5, current_request)						#start the thread that each N seconds asks to the main thread
#	c.start() 													#to send a request to the MCU

	p = perpetualTimer(20, pressure_request)						#start the thread that each N seconds asks to the main thread
	p.start() 													#to send a request to the MCU
	latchup = [0,0,0]
	while 1:													#main loop
		
		if not q.empty():										#if there is a request to the MCU in queue
			q_get = q.get()
			buffer = serial_request (ser, q_get)				#send the command to the MCU and read back the result
			if b'!' in buffer:									#check if meanwhile a letch-up occurred
				writeLogFile(out_file, "Latch-up!!")
				latchup=handle_latchup(ser)						#if yes, handle it and throw away the other information
				writeLogFile(out_file, "Latch-up stat: N(1.8, 3.3) = (%d, %d) deltaTime = %d ms \n" % (latchup[0], latchup[1], latchup[2]))
				print ("Latch-up!! N(1.8, 3.3) = (%d, %d) deltaTime = %d ms\n" % (latchup[0], latchup[1], latchup[2]))			#the first string is referred to the 1.8V and the second to 3.3V
				#winsound.Beep(SoundFreq, SoundDuration)
			else:
				if q_get == b't':
					values = separate_string( buffer )				#if there wasn't , separate the string in a list of values 
					temperatures = get_temp_values (values)			#convert the string in the value
					print ("t: (DC3.3, ADC, ASIC, DC1.8asic, FPGA) = (%.1f, %.1f, %.1f, %.1f, %.1f)" %\
						(temperatures[0],temperatures[1],temperatures[2],temperatures[3],temperatures[4]))
					writeLogFile(out_file, "t: (DC3.3, ADC, ASIC, DC1.8asic, FPGA) = (%.1f, %.1f, %.1f, %.1f, %.1f)" %\
						(temperatures[0],temperatures[1],temperatures[2],temperatures[3],temperatures[4]))
					writeLogFile(out_file, "t r: "+str(values)) # adding raw values
				elif q_get == b'c':
					values = separate_string( buffer )				#if there wasn't , separate the string in a list of values 
					current = get_current_value (values)			#convert the string in the value
					print ("c (1.8, 3.3) = (%.1f, %.1f)" % (current[0], current[1]))
					writeLogFile(out_file, "c (1.8, 3.3) = (%.1f, %.1f)" % (current[0], current[1]))
					writeLogFile(out_file, "c r: "+str(values)) # adding raw values
				elif q_get == b'p':
					values = separate_string( buffer )				#if there wasn't , separate the string in a list of values 
					pressure = get_pressure_value (values)			#convert the string in the value
					print ("p  = %.1f mbar" % (pressure))
					writeLogFile(out_file, "p  = %.1f mbar" % (pressure))
					writeLogFile(out_file, "p r: "+str(values)) # adding raw values
		byteincoming = ser.inWaiting()							
		if byteincoming != 0:									#if a byte is incoming w/o any request is a Latch-up event
			buffer = ser.read(byteincoming)						#read the serial buffer
			if b'!' in buffer:									#check if it is a latch-up 
				writeLogFile(out_file, "Latch-up!!")
				latchup = handle_latchup(ser)					#if yes, handle it
				writeLogFile(out_file, "Latch-up stat: N(1.8, 3.3) = (%d, %d) deltaTime = %d ms \n" % (latchup[0], latchup[1], latchup[2]))
				print ("Latch-up!! N(1.8, 3.3) = (%d, %d) deltaTime = %d ms\n" % (latchup[0], latchup[1], latchup[2]))          #the first string is referred to the 1.8V and the second to 3.3V
				#winsound.Beep(SoundFreq, SoundDuration)
except (KeyboardInterrupt, SystemExit):							#on ctrl + C signal
		t.cancel()												#close the thread
		#c.cancel()												#close the thread
                p.cancel()												#close the thread
		
		ser.close ()											#close the serial port and exit
		elapsed_time = time.time() - start_time
		print ("Serial port " + ser.portstr + " closed"+"\n")
		writeLogFile(out_file,  "Serial port " + str(ser.portstr) + " closed")
		# latchup rate = N_latchup/(Time - N*Recovery_time)
		latchup_rate = np.array([latchup[0], latchup[1]])
		latchup_rate = latchup_rate/(elapsed_time - latchup_rate*RECOVERY_TIME) # Hz
		summary_str = "Run statistics: N_latchup(1.8, 3.3) = (%d, %d)" % (latchup[0], latchup[1]) + \
			" Elapsed time= "+ str(elapsed_time) + " Rate=" + str(latchup_rate) + "\n"
		print ( summary_str)
		writeLogFile(out_file, summary_str)
		sys.exit()
