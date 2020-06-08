from serial import Serial
from threading import Thread
from time import sleep, time
from Helper import Helper

class Arduino(Thread):
	def __init__(self, port, baud):
		Thread.__init__(self)
		self.device = Serial(port, baud)
		self.isRunning = True
	
	def readoutput_all(self):
		file = open("/home/martin/aktuell/aripetemp/t"+str(round(time()%100000))+".raw", "w")
		self.device.flushInput()
		while self.isRunning:
			s = self.device.read_all().decode()
			file.write(s)
		file.close()
	
	def run(self):
		pass
	
h = Helper()
a = Arduino(h.getSerialPorts()[0][0], 9600)
a.start()
a.readoutput_all()
print("Holla")
sleep(5)
a.isRunning = False