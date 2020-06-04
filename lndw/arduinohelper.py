import serial

class ArduinoHelper():
    def __init__(self, ardport, noe, scmin, scmax):
        self.arduinoport = ardport
        self.number_of_steps = noe
        self.scale_minimum = scmin
        self.scale_maximum = scmax
        self.distance_per_step = abs(scmax-scmin)/self.number_of_steps
        self.arduino = serial.Serial(port=self.arduinoport, baudrate=9600)
        self.min_smaller_max = scmin < scmax

    def getDistance(self):
        self.arduino.flushInput()
        misses = 0
        errorous = True
        while misses < 10 and errorous:
            try:
                dis = int(float(str(self.arduino.readline()).split("\\")[0].split(" ")[1]))
                errorous = False
            except:
                misses += 1
        if errorous:
            return -1
        if self.min_smaller_max:
            rv = (dis - self.scale_minimum)/self.distance_per_step
        else:
            rv = (self.scale_minimum-dis)/self.distance_per_step
        if rv < 0:
            return 0
        if rv > self.number_of_steps:
            return self.number_of_steps
        return rv