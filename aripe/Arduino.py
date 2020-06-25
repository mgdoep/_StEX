from serial import Serial
from threading import Thread
from time import sleep, time
from Helper import Helper


class Arduino(Thread):
	def __init__(self, port, baud):
		Thread.__init__(self)
		self.device = Serial(port, baud)
		self.isRunning = True
		self.RawFileName = ""
		self.currentValues = []
	
	"""
	readContiniously
	Reads the input from the Arduino and writes it to a temporary file, the file name is returned.
	Call Data.getValuesFromRawFile afterwards to import the data in the container!
	Parameter:
	- tempFolder: directory of the temporary file
	"""
	def readContinously(self, tempFolder, sleep_time=1.0, **kwargs):
		self.RawFileName = tempFolder + "/t"+str(round(time()%100000))+".raw"
		stopafter = False
		file = open(self.RawFileName, "w")
		if "time" in kwargs.keys() and kwargs["time"] is not None:
			duration = float(kwargs["time"])
			stopafter = True
		self.device.flushInput()
		if stopafter:
			start = time()
			while time()-start < duration:
				s = self.device.read_all().decode()
				self.currentValues = s.split("\r")[-1]
				file.write(s)
				sleep(sleep_time)
		else:
			while self.isRunning:
				s = self.device.read_all().decode()
				file.write(s)
				sleep(sleep_time)
		file.close()
	
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
	
	def run(self):
		pass

# tempFolder = "/home/martin/aktuell/aripetemp/"
