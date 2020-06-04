#https://stackoverflow.com/questions/24214643/python-to-automatically-select-serial-ports-for-arduino

import serial.tools.list_ports as lipo

def getPorts():
    rv = []
    ports = list(lipo.comports())
    for p in ports:
        rv.append(str(p).split(" - "))
    return rv