import sys
import serial
import Queue
import datetime

from lib_monitor import *
#-------------------------------------------------------------------------------------------------------------------
def temperature_request():										# put in the queue the request to read the temperatures				
	q.put("t")

#-------------------------------------------------------------------------------------------------------------------
q = Queue.Queue()												#define a queue for multi-thread messaging
out_file = open(str(datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))+"_test.txt","w")									#open the log file
try:
	ser = serial.Serial("../../../../../../../dev/ttyS4")  		#select the serial port
	ser.baudrate = 9600 										#set baudrate to 9600bps
	
																
	if not ser.isOpen():										#check if the port is not already open
		ser.open() 												#open serial port
		
	if  ser.isOpen():
		com_num = ser.portstr
		print ("Serial port " + com_num + " opened"+"\n")
		out_file.write(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+"\t"+"Serial port " + str(com_num) + " opened"+"\n")
	else:														#if the port is still closed, exit
		print('Error: impossible to open the serial port'+"\n")
		out_file.write(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+"\t"+'Error: impossible to open the serial port'+"\n")
		sys.exit()
	
	
	t = perpetualTimer(1 ,temperature_request)					#start the thread that each N seconds asks to the main thread
	t.start() 													#to send a request to the MCU

	while 1:													#main loop
		
		if not q.empty():										#if there is a request to the MCU in queue
			buffer = serial_request (ser, q.get())				#send the command to the MCU and read back the result
			if '!' in buffer:									#check if meanwhile a letch-up occurred
				latchup=handle_latchup(ser)						#if yes, handle it and throw away the other information
				out_file.write(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+"\t"+"Latch-up!!"+"\n")
				print ("Latch-up!!"+"\n")
				print (latchup)									#the first string is referred to the 1.8V and the second to 3.3V
				out_file.write(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+"\t"+str(latchup)+"\n")	
			else:												
				values = separate_string( buffer )				#if there wasn't , separate the string in a list of values 
				temperatures = get_temp_values (values)			#convert the string in the value
				print (temperatures)
				out_file.write(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+"\t"+str(temperatures)+"\n")
				
		byteincoming = ser.inWaiting()							
		if byteincoming != 0:									#if a byte is incoming w/o any request is a Latch-up event
			buffer = ser.read(byteincoming)						#read the serial buffer
			if '!' in buffer:									#check if it is a latch-up 
				latchup = handle_latchup(ser)					#if yes, handle it
				out_file.write(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+"\t"+"Latch-up!!"+"\n")
				print ("Latch-up!!"+"\n")
				print (latchup)									#the first string is referred to the 1.8V and the second to 3.3V
				out_file.write(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+"\t"+str(latchup)+"\n")	
				
except (KeyboardInterrupt, SystemExit):							#on ctrl + C signal
		t.cancel()												#close the thread
		
		ser.close ()											#close the serial port and exit
		print ("Serial port " + ser.portstr + " closed"+"\n")
		out_file.write(str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))+"\t"+"Serial port " + str(ser.portstr) + " closed"+"\n")
		out_file.close()
		sys.exit()






