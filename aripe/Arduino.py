from serial import Serial
from threading import Thread, Event
from time import sleep, time
import sys
import os
path = os.getcwd()
import importlib
Helper = importlib.import_module("Helper", path+"Helper.py")


class Arduino(Thread):
	def __init__(self, port, baud, helper, stopevent, GUI):
		Thread.__init__(self)
		self.device = Serial(port, baud)
		self.helper = helper
		self.StopEvent = stopevent
		self.GUI = GUI
		self.Running = True
		self.RawFileName = ""
		
	
	"""
	readContiniously
	Reads the input from the Arduino and writes it to a String.
	Call Data.getValuesFromRawFile afterwards to import the data in the container!
	Parameter:
	- tempFolder: directory of the temporary file
	- sleep_time: Time between each reading attempt to ensure new values can be read
	"""
	def readContinously(self, tempFolder, sleep_time=0.4, **kwargs):
		self.RawFileName = tempFolder + "/t"+str(round(time()%100000))+".raw"
		stopafter = False
		cvs = ""
		s = ""
		if "time" in kwargs.keys() and kwargs["time"] is not None:
			duration = float(kwargs["time"])
			stopafter = True
		self.device.flushInput()
		if stopafter:
			start = time()
			cvs = ""
			while time()-start < duration and self.helper.ArduinoIsRunning:
				s = self.device.read_all().decode()
				cvs += s
				if self.helper.ArduinoIsRunning:				#Zur Sicherheit, dass nicht geschrieben wird, während GUI versucht zu importieren
					file = open(self.RawFileName, "a")
					file.write(s)
					file.close()
				try:
					cvss = cvs.split("\n")[0]
					if len(cvss) > 0:
						self.GUI.updateLive(cvs.split("\n")[0])
						cvs = ""
				except:
					pass
				sleep(0.4)
		else:
			while self.Running:
				s = self.device.read_all().decode()
				cvs += s
				file = open(self.RawFileName, "a")
				file.write(s)
				file.close()
				if self.StopEvent.is_set():
					break
				try:
					#self.helper.currentValues = cvs.split("\n")[-1]
					self.GUI.updateLive(cvs.split("\n")[0])
					cvs = ""
				except:
					pass
				sleep(0.4)
			#sleep(0.2)
	
	"""
	readCurrent
	Reads the current input and returns a list with the columns in string format
	Parameter:
	- protocolString: protocol string for correct data
	- seperator: character seperating the columns, default value: " " (blank space)
	"""
	
	def readCurrent(self, protocolString, seperator=" "):
		rv = []
		self.device.flushInput()
		misses = 0
		errorous = True
		while misses < 10 and errorous:
			try:
				line = str(self.device.readline().decode()).split(seperator)
				if line[0].strip() == protocolString and ("\n" in line[-1] or "\r" in line[-1]): #Checks whether the line is complete
					errorous = False
					return line
			except:
				misses += 1
		return []
	
	def getRawFileName(self):
		return self.RawFileName
	
	def run(self):
		pass
	
	

# tempFolder = "/home/martin/aktuell/aripetemp/"
