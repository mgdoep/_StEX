'''

Skript zur Kalibrierung des Experiments "Funktionen laufen" zur Langen Nacht der Wissenschaften 2019
Es erstellt die Datei calib.txt mit folgenden Daten:

- port: USB-Port des Arduino
- steps: Wertebereich der Funktion W=[0, steps]
- min: Abstand zum Wert 0
- max: Abstand zum Wert steps

Auswahl des Ports werden (sofern Port-Wahl erfolgreich, d.h. Verbindung ist möglich und der Arduino sendet das richtige Messprotokoll (DST bzw. DSTE) folgende Schritte ausgeführt:
- Auswahl des Maximalwerts des Wertebereichs
- Festlegung von min und max
- Sind min und max festgelegt, schaltet die Entfernungsanzeige auf Funktionswerte um, sodass man leichter die Striche anbringen kann.

Das Skript wurde von Martin Döpel erstellt (post@martin-doepel.de).

Weimar/Jena, Oktober/November 2019

'''

from PyQt5 import QtCore, QtGui, QtWidgets
import serial.tools.list_ports as lipo
import serial
import time
import sys

class Helper():
    def __init__(self):
        self.port = ""
        self.steps = 5
        self.min = -1.0
        self.max = -1.0
        self.ser = ""

        self.connected = False

    def getPorts(self):
        rv = []
        ports = list(lipo.comports())
        for p in ports:
            rv.append(str(p).split(" - "))
        return rv

    def correctProtocol(self):
        try:
            self.ser = serial.Serial(port=self.port, baudrate=9600)
        except serial.serialutil.SerialException:
            return 1
        stime = time.time()
        misses = 0
        self.ser.flushInput()
        while (time.time()-stime < 4) and (misses < 7):
            proto = str(self.ser.readline()).split(" ")[0]
            if (proto == "b\'DST") or (proto == "b\'DSTE"):
                self.ser.flushInput()
                self.connected = True
                return 0
            misses += 1
        return 2

    def saveData(self):
        file = open("calib.cal", "w")
        s = "port "+self.port+":\n"
        s += "steps "+str(self.steps)+"\n"
        s += "min " + str(self.min) + "\n"
        s += "max " + str(self.max)
        file.write(s)
        file.close()
        self.ser.close()

    def getValues(self):
        while True and self.connected:
            try:
                strg = self.ser.readline()
                d = int(float(str(self.ser.readline()).split("\\")[0].split(" ")[1]))
                return d
            except:
                return -1
        return -1


class OFlaeche(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi()

    def setupUi(self):
        self.h = Helper()
        self.cdst = 0.0
        self.font1 = QtGui.QFont()
        self.font1.setPointSize(12)
        self.font2 = QtGui.QFont()
        self.font2.setPointSize(40)

        self.resize(350, 350)

        self.setWindowTitle("Kalibrierung Funktionen laufen")


        self.HeadArduino = QtWidgets.QLabel(self)
        self.HeadArduino.setText("Arduino-Port")
        self.HeadArduino.setGeometry(QtCore.QRect(30, 10, 131, 16))
        self.HeadArduino.setFont(self.font1)

        self.Head2 = QtWidgets.QLabel(self)
        self.Head2.setText("Maximaler Funktionswert")
        self.Head2.setGeometry(QtCore.QRect(30, 70, 191, 16))
        self.Head2.setFont(self.font1)
        self.Head2.setVisible(False)

        self.Head3 = QtWidgets.QLabel(self)
        self.Head3.setText("Position Extremwerte")
        self.Head3.setGeometry(QtCore.QRect(30, 140, 191, 16))
        self.Head3.setFont(self.font1)
        self.Head3.setVisible(False)

        self.arduinooptions = QtWidgets.QComboBox(self)
        self.arduinooptions.setGeometry(QtCore.QRect(30, 30, 181, 22))
        for p in self.h.getPorts():
            self.arduinooptions.addItem(p[1]+" - "+p[0])

        self.arduinochoose = QtWidgets.QPushButton(self)
        self.arduinochoose.setGeometry(QtCore.QRect(230, 30, 75, 23))
        self.arduinochoose.setObjectName("arduinochoose")
        self.arduinochoose.setText("wählen")
        self.arduinochoose.clicked.connect(self.AChoose)

        self.mindst = QtWidgets.QLabel(self)
        self.mindst.setGeometry(QtCore.QRect(130, 170, 151, 20))
        self.mindst.setObjectName("mindst")
        self.mindst.setText("noch nicht gewählt")
        self.mindst.setVisible(False)

        self.minchoose = QtWidgets.QPushButton(self)
        self.minchoose.setGeometry(QtCore.QRect(30, 170, 75, 23))
        self.minchoose.setObjectName("minchoose")
        self.minchoose.setText("Minimum")
        self.minchoose.clicked.connect(self.MiCAction)
        self.minchoose.setVisible(False)

        self.maxchoose = QtWidgets.QPushButton(self)
        self.maxchoose.setGeometry(QtCore.QRect(30, 210, 75, 23))
        self.maxchoose.setObjectName("maxchoose")
        self.maxchoose.setText("Maximum")
        self.maxchoose.clicked.connect(self.MaCAction)
        self.maxchoose.setVisible(False)

        self.maxdst = QtWidgets.QLabel(self)
        self.maxdst.setGeometry(QtCore.QRect(130, 210, 151, 20))
        self.maxdst.setObjectName("maxdst")
        self.maxdst.setText("noch nicht gewählt")
        self.maxdst.setVisible(False)

        self.schritte = QtWidgets.QComboBox(self)
        self.schritte.setGeometry(QtCore.QRect(30, 100, 69, 22))
        self.schritte.setObjectName("schritte")
        self.schritte.addItem("2")
        self.schritte.addItem("3")
        self.schritte.addItem("4")
        self.schritte.addItem("5")
        self.schritte.addItem("6")
        self.schritte.addItem("7")
        self.schritte.setCurrentIndex(3)
        self.schritte.currentIndexChanged.connect(self.StepChoose)
        self.schritte.setVisible(False)

        self.currdst = QtWidgets.QLabel(self)
        self.currdst.setGeometry(QtCore.QRect(130, 250, 201, 41))
        self.currdst.setFont(self.font2)
        self.currdst.setObjectName("currdst")
        self.currdst.setText("nn")
        self.currdst.setVisible(False)

        self.calibexit = QtWidgets.QPushButton(self)
        self.calibexit.setGeometry(QtCore.QRect(30, 310, 181, 23))
        self.calibexit.setObjectName("calibexit")
        self.calibexit.setText("Kalibrierung beenden")
        self.calibexit.clicked.connect(self.FinishAll)
        self.calibexit.setVisible(False)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.updateDSTValue)
        self.timer.start(20)
        self.show()

    def updateDSTValue(self):
        dst = self.h.getValues()
        if dst == -1:
            self.currdst.setText("Error")
        elif (self.h.min < 0.0 or self.h.max < 0.0):
            self.cdst = dst
            self.currdst.setText(str(dst))
        else:
            if (self.h.min < self.h.max):
                schrittweite = (self.h.max - self.h.min) / self.h.steps
                wert = (dst - self.h.min)/schrittweite
            else:
                schrittweite = (self.h.min - self.h.max) / self.h.steps
                wert = (self.h.min - dst) / schrittweite
            self.currdst.setText(str(wert))
            self.calibexit.setVisible(True)

    def MiCAction(self):
        self.h.min = self.cdst
        self.mindst.setText(str(self.h.min))

    def MaCAction(self):
        self.h.max = self.cdst
        self.maxdst.setText(str(self.h.max))

    def StepChoose(self):
        self.h.steps = int(self.schritte.currentText())

    def AChoose(self):
        self.h.port = str(self.arduinooptions.currentText()).split(" - ")[1]
        if self.h.correctProtocol() == 0:
            self.Head2.setVisible(True)
            self.Head3.setVisible(True)
            self.currdst.setVisible(True)
            self.schritte.setVisible(True)
            self.maxdst.setVisible(True)
            self.maxchoose.setVisible(True)
            self.minchoose.setVisible(True)
            self.mindst.setVisible(True)
            self.schritte.setVisible(True)

        elif self.h.correctProtocol() == 2:
            self.h.ser.close()
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("Falsches Protokoll")
            msg.setInformativeText("Der angeschlossene Arduino sendet nicht das korrekte Protokoll. Bitte versuchen Sie es noch einmal erneut und prüfen Sie bei nochmaligem Fehler das Programm des Arduino.")
            msg.setWindowTitle("Protokollfehler")
            msg.exec_()
        else:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("Hardware-Problem")
            msg.setInformativeText("Verbindung zum Arduino kann nicht hergestellt werden.")
            msg.setWindowTitle("Verbindungsfehler")
            msg.exec_()

    def FinishAll(self):
        self.h
        self.h.saveData()
        self.close()


if __name__== "__main__":
    app = QtWidgets.QApplication([])
    ex = OFlaeche()
    sys.exit(app.exec_())