from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from time import sleep
from PyQt5.QtGui import QIcon
import sys
import os
path = os.getcwd()
import importlib
Project = importlib.import_module("Project", path+"Project.py")
Helper = importlib.import_module("Helper", path+"Helper.py")
Arduino = importlib.import_module("Arduino", path+"Arduino.py")

class GUI(QtWidgets.QMainWindow):
	def __init__(self):
		super().__init__()
		self.step = 0
		self.misc = Helper.Helper()
		self.Project = None
		#self.Arduino = None
		self.Value = 0
		self.MeasureMode = -1
		self.currentArduinoValues = []
		self.setupUi()
	
	def setupUi(self):
		self.font_bold = QtGui.QFont()
		self.font_bold.setBold(True)
		self.font_Bedienelemente = QtGui.QFont()
		self.font_Bedienelemente.setPointSize(12)
		self.font_Bedienelemente_bold = QtGui.QFont()
		self.font_Bedienelemente_bold.setBold(True)
		self.font_LiveWerte = QtGui.QFont()
		self.font_LiveWerte.setPointSize(24)
		
		self.font_KalLabel = QtGui.QFont("Times", 16)
		
		self.setWindowTitle("aripe")
		
		#menuebar
		self.loadProject = QtWidgets.QAction("Projekt öffnen", self)
		self.loadProject.setShortcut("Ctrl+O")
		self.loadProject.triggered.connect(self.getProject)
		
		self.addContrib = QtWidgets.QAction("Mitwirkende", self)
		self.addContrib.setShortcut("Ctrl+M")
		self.addContrib.triggered.connect(self.addContribuor)
		self.addContrib.setDisabled(True)
		
		self.showVariables = QtWidgets.QAction("Variablen anzeigen", self)
		self.showVariables.triggered.connect(self.VariableTable)
		self.showVariables.setDisabled(True)
		
		menuebar = self.menuBar()
		projectMenue = menuebar.addMenu("Projekt")
		projectMenue.addAction(self.loadProject)
		projectMenue.addAction(self.addContrib)
		projectMenue.addAction(self.showVariables)
		
		#buttons
		self.button_startMeasurement = QtWidgets.QPushButton("Messung starten", self)
		self.button_startMeasurement.adjustSize()
		self.button_startMeasurement.setDisabled(True)
		self.button_startMeasurement.move(20,30)
		self.button_startMeasurement.setVisible(False)
		
		self.button_endMeasurement = QtWidgets.QPushButton("Messung beenden", self)
		self.button_endMeasurement.adjustSize()
		self.button_endMeasurement.setDisabled(True)
		self.button_endMeasurement.move(20,70)
		self.button_endMeasurement.setVisible(False)
		
		self.button_Kalibriere = QtWidgets.QPushButton("Kalibriere", self)
		self.button_Kalibriere.setVisible(False)
		self.button_Beenden = QtWidgets.QPushButton("Beenden", self)
		self.button_Beenden.setVisible(False)
		
		
		self.Label_LiveWertName = QtWidgets.QLabel(self)
		self.Label_LiveWertName.move(20,30)
		self.Label_LiveWertName.setFont(self.font_KalLabel)
		self.Label_LiveWertName.setVisible(False)
		
		self.Label_LiveWert = QtWidgets.QLabel(self)
		self.Label_LiveWert.setText("xyz")
		self.Label_LiveWert.move(20, 100)
		self.Label_LiveWert.setFont(self.font_LiveWerte)
		self.Label_LiveWert.setVisible(False)
		
		self.buttons_output = []
		
		
		self.liveValueItem = 0
		self.liveValueText = ""
		self.liveValueVariable = ""
		self.currentLiveValue = 0.0
		self.isSet = False
		self.itemToCalibrate = 0
		self.NumberOfItemsToCalibrate = 0
		
		
		self.timer = QtCore.QTimer(self)
		self.timer.timeout.connect(self.getLiveValue)
		
		self.manInputFields, self.manInputLabels, self.manInputVarNames, self.manErrorFields, self.manErrorLabels = [], [], [], [], []
		self.LiveValueMeter, self.LiveValueLabel, self.LiveValueColumns = [], [], []
		self.ArdMeasureCols = []
			
		#self.ManualInputButton.setVisible(False)
		
		#print(self.ManualInput1_Label.size().width())
		#self.setMouseTracking(True)
		
		self.inProgress = True
		

		self.setGeometry(100, 100, 600, 600)
		self.show()
		
	def showV(self):
		for i in range(len(self.manInputFields)):
			print(i, self.manInputFields[i].text())
			
	def addContribuor(self):
		pass
		
		
	def getProject(self):
		name = QFileDialog.getOpenFileName(self, "Projektdatei wählen", "~/")[0]
		if name != "":
			self.Project = Project.Project(name)
			if self.Project.succLoad():
				self.addContrib.setDisabled(False)
				self.loadProject.setDisabled(True)
				if len(self.Project.getName()) > 0:
					self.setWindowTitle("aripe - " + self.Project.getName())
				if self.Project.usesArduino():
					self.getArduino()
				outputforms = self.Project.getOutputs()
				
				if len(outputforms) > 0:
					i = 0
					while i < len(outputforms):
						x = 20
						y = 30 + 40 * i
						if outputforms[i]["type"].lower() == "xls":
							b = QtWidgets.QPushButton("Excel-Tabelle", self)
						elif outputforms[i]["type"].lower() == "csv":
							b = QtWidgets.QPushButton("CSV-Tabelle", self)
						elif outputforms[i]["type"].lower() == "plot":
							if "fit" in outputforms[i].keys():
								b = QtWidgets.QPushButton("Diagramm mit Fit", self)
							else:
								b = QtWidgets.QPushButton("Diagramm", self)
						elif outputforms[i]["list"] and len(outputforms) < 2:
							b = QtWidgets.QPushButton("Liste", self)
						elif outputforms[i]["table"] and len(outputforms) < 2:
							b = QtWidgets.QPushButton("Tabelle", self)
						else:
							i += 1
							continue
						b.adjustSize()
						b.move(x, y)
						#b.setDisabled(True)
						b.setVisible(False)
						b.clicked.connect(self.getOutput)
						self.buttons_output.append([b, (x,y)])
						i += 1
				self.showVariables.setDisabled(False)
			self.step += 1 #is now 1
			self.itemToCalibrate = 0
			self.NumberOfItemsToCalibrate = len(self.Project.calibrationFor())
			if self.NumberOfItemsToCalibrate == 0:
				self.step = 2
				self.startMeasurement()
			self.calibrate()
				#self.buttons_output[1][0].setVisible(True)
				
	def calibrate(self):
		if self.itemToCalibrate < self.NumberOfItemsToCalibrate:
			c = self.Project.calibrationFor()[self.itemToCalibrate]
			self.isSet = False
			self.liveValueText = "Kalibriere Variable "+c["name"]
			self.liveValueItem = self.Project.getArduinoColumn(c["name"])
			self.liveValueVariable = c["name"]
			self.isSet = False
			self.timer.setSingleShot(True)
			self.timer.start(20)
		
			
	
	def getLiveValue(self):
		line = self.Arduino.readCurrent(self.Project.ardProtocol, seperator=self.Project.ardSeperator)
		
		if self.step == 1:
			self.Label_LiveWertName.setText(self.liveValueText)
			self.Label_LiveWertName.adjustSize()
			self.Label_LiveWertName.setVisible(True)
			
			self.button_Kalibriere.adjustSize()
			self.button_Kalibriere.move(20, 150)
			self.button_Kalibriere.setVisible(True)
			self.button_Kalibriere.clicked.connect(self.saveLiveValue)
		
			if len(line) > 0:
				self.currentLiveValue = line[self.liveValueItem].strip()
				self.Label_LiveWert.setText(self.currentLiveValue)
				self.Label_LiveWert.setVisible(True)
				if self.itemToCalibrate < self.NumberOfItemsToCalibrate:
					self.calibrate()
				else:
					self.timer.stop()
					self.step += 1
					self.Label_LiveWert.setVisible(False)
					self.Label_LiveWertName.setVisible(False)
					self.button_Kalibriere.setVisible(False)
					self.startMeasurement()
			else:
				self.currentLiveValue = "NIL"
				self.Label_LiveWert.setText("Fehler")
				self.Label_LiveWert.setVisible(True)
				if self.itemToCalibrate < self.NumberOfItemsToCalibrate:
					self.calibrate()
					
		if self.step == 2 and self.MeasureMode == 0:
			self.currentArduinoValues = self.Arduino.readCurrent(self.Project.ardProtocol, seperator=self.Project.ardSeperator)
			for i in range(self.number_live_values):
				self.LiveValueMeter[i].setText(self.currentArduinoValues[self.LiveValueColumns[i]])
			self.timer.setSingleShot(True)
			self.timer.start(10)
			
			
			
			
		
	
	def saveLiveValue(self):
		if self.step == 1 and self.currentLiveValue != "NIL" and not self.isSet:
				self.Project.setCalibration({"name": self.liveValueVariable, "cvalue": float(self.currentLiveValue)})
				self.itemToCalibrate += 1
				self.isSet = True
	
	
	def EndMeasure(self):
		self.timer.stop()
		if self.MeasureMode == 0:
			for v in self.manInputFields:
				v.setVisible(False)
			for v in self.manInputLabels:
				v.setVisible(False)
			for v in self.manErrorFields:
				if v is not None:
					v.setVisible(False)
			for v in self.manErrorLabels:
				v.setVisible(False)
		for v in self.LiveValueMeter:
			v.setVisible(False)
		for v in self.LiveValueLabel:
			v.setVisible(False)
		self.step = 3
		self.Project.MeasurementPostProcessing()
	
	def Measure(self):
		valimport = []
		if self.MeasureMode == 0:
			for i in range(self.number_arduino_variables):
				if self.ArdMeasureCols[i] is not None:
					vto = {"name": self.ArdMeasureCols[i], "value": self.currentArduinoValues[i], "error": 0.0}
					valimport.append(vto)
			for i in range(self.number_manual_variables):
				vto = {"name": self.manInputVarNames[i], "value": self.manInputFields[i].text(), "error": 0.0}
				if self.manErrorFields[i] is not None:
					vto["error"] = self.manErrorFields[i].text()
					self.manErrorFields[i].setText("")
				valimport.append(vto)
				self.manInputFields[i].setText("")
			self.Project.addManualValues(valimport)
			
	def startMeasurement(self):
		if self.step == 2:
			self.vars, self.number_manual_variables, self.number_live_values = self.Project.ManualArduinoVariables()
			i = 0
			breite_manual = 0
			hoehe_manuallabel = 0
			hoehe_manualfield = 0
			
			self.button_Beenden.setVisible(True)
			
			#Init fields and labels for manual input
			while i < self.number_manual_variables:
				self.MeasureMode = 0
				if i == 0:
					self.ManualInputButton = QtWidgets.QPushButton(self)
					self.ManualInputButton.setText("Wert[e] speichern")
					self.ManualInputButton.adjustSize()
					self.ManualInputButton.setVisible(True)
					self.ManualInputButton.clicked.connect(self.Measure)
					y = 40+60*self.number_manual_variables
					self.ManualInputButton.move(20, y)
					self.button_Beenden.move(300, y)
					self.button_Beenden.clicked.connect(self.EndMeasure)
					self.ManualInputButton.resize(QtCore.QSize(self.ManualInputButton.size().width()+10, self.button_Beenden.size().height()))
				f = QtWidgets.QLineEdit("", self)
				f.resize(80, f.size().height())
				f.setVisible(True)
				hoehe_manualfield = f.size().height()
				if self.vars["manual"][i]["getErrorValue"]:
					e = QtWidgets.QLineEdit("", self)
					e.setVisible(True)
					e.resize(30, e.size().height())
					self.manErrorFields.append(e)
					el = QtWidgets.QLabel(self)
					el.setVisible(True)
					el.setFont(self.font_bold)
					el.setText("\u00B1")
					el.move(200, 35+60*i)
					self.manErrorLabels.append(el)
				else:
					self.manErrorFields.append(None)
					self.manErrorLabels.append(None)
					
				l = QtWidgets.QLabel(self)
				l.setVisible(True)
				l.setFont(self.font_bold)
				l.setText(self.vars["manual"][i]["name"] + " (in " + self.vars["manual"][i]["unit"] + ")")
				l.adjustSize()
				b, h = l.size().width(), l.size().height()
				if breite_manual < b:
					breite_manual = b
				if hoehe_manuallabel < h:
					hoehe_manuallabel = h
				l.move(20, 40+60*i)
				self.manInputFields.append(f)
				self.manInputLabels.append(l)
				self.manInputVarNames.append(self.vars["manual"][i]["name"])
				i += 1
			x = breite_manual + 40
			k = (hoehe_manualfield-hoehe_manuallabel)//2
			for i in range(self.number_manual_variables):
				self.manInputFields[i].move(x, 40+i*60-k)
				if self.manErrorFields[i] is not None:
					self.manErrorFields[i].move(220, 40+i*60-k)
			
			if self.number_live_values > 0:
				self.timer.setInterval(20)
				i = 0
				breite = 0
				x_base = 300
				for v in self.vars["arduino"]:
					if v["live"]:
						self.LiveValueColumns.append(v["ardCol"])
						m = QtWidgets.QLabel(self)
						m.setFont(self.font_LiveWerte)
						m.setVisible(True)
						m.setText("0.0")
						m.resize(150, m.size().height())
						l = QtWidgets.QLabel(self)
						l.setFont(self.font_bold)
						l.setText(v["name"]+" (in "+v["unit"]+") ")
						if breite < l.size().width():
							breite = l.size().width()
						l.setVisible(True)
						l.move(x_base, 40+60*i)
						self.LiveValueMeter.append(m)
						self.LiveValueLabel.append(l)
						i += 1
				x = x_base + 20 + breite
				k = (self.LiveValueMeter[0].size().height() - self.LiveValueLabel[0].size().height()) // 2
				for i in range(i):
					self.LiveValueMeter[i].move(x, 40+60*i-k)
			av = 0
			for v in self.vars["arduino"]:
				if v["ardCol"]+1 > av:
					av = v["ardCol"]+1
			self.ArdMeasureCols = [None]*av
			self.number_arduino_variables = av
			for v in self.vars["arduino"]:
				self.ArdMeasureCols[v["ardCol"]] = v["name"]
			if self.MeasureMode != 0:
				self.MeasureMode = 1
			self.timer.start(10)
		
		
			
		
		
	def getValue(self):
		pass
	def getOutput(self):
		print(self.sender().pos().y())
		pass					#TODO: Implement the outputs, nr gives index in list
	
	def VariableTable(self):
		box = QtWidgets.QGroupBox("Variablen")
		variablen = self.Project.getVariables()
		tabelle = QtWidgets.QTableWidget()
		tabelle.setRowCount(len(variablen)+1)
		tabelle.setColumnCount(2)
		tabelle.setItem(0,0, QtWidgets.QTableWidgetItem("Name"))
		tabelle.setItem(0,1, QtWidgets.QTableWidgetItem("Einheit"))
		tabelle.item(0,0).setFont(self.font_bold)
		tabelle.item(0,1).setFont(self.font_bold)
		i = 0
		while i < len(variablen):
			tabelle.setItem(i+1,0, QtWidgets.QTableWidgetItem(variablen[i]["name"]))
			tabelle.setItem(i + 1, 1, QtWidgets.QTableWidgetItem(variablen[i]["unit"]))
			i += 1
		vbox = QtWidgets.QVBoxLayout()
		vbox.addWidget(tabelle)
		box.setLayout(vbox)
		box.setVisible(True)
		
		
	def getArduino(self):
		p = self.misc.getSerialPorts()
		if len(p) == 1 and self.Project.getBaud() > 0:
			self.Arduino = Arduino.Arduino(p[0][0], self.Project.getBaud())
			self.Arduino.start()

app = QtWidgets.QApplication(sys.argv)
ex = GUI()
sys.exit(app.exec_())