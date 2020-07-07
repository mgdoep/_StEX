from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from time import time, sleep
from threading import Event
from PyQt5.QtGui import QIcon
import sys
import os
path = os.getcwd()
import importlib
Project = importlib.import_module("Project", path+"Project.py")
Helper = importlib.import_module("Helper", path+"Helper.py")
Arduino = importlib.import_module("Arduino", path+"Arduino.py")

matplot_success = True
try:
	import matplotlib.pyplot as plt
except ImportError:
	matplot_success = False

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
		self.isRunning = False
		self.startTime = 0
		self.ArduinoStopEvent = Event()
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
		
		self.font_KalLabel = self.font_bold
		self.font_Countdown = QtGui.QFont()
		self.font_Countdown.setPointSize(36)
		self.font_Countdown.setBold(True)

		self.setWindowTitle("aripe")
		self.setGeometry(100,100,600,600)
		self.setMinimumSize(600, 600)
		self.ArduinoIsRunning = True
		
		#menuebar
		self.loadProject = QtWidgets.QAction("Projekt öffnen", self)
		self.loadProject.setShortcut("Ctrl+O")
		self.loadProject.triggered.connect(self.getProject)
		
		self.addContrib = QtWidgets.QAction("Mitwirkende", self)
		self.addContrib.setShortcut("Ctrl+M")
		self.addContrib.triggered.connect(self.addContribuor)
		self.addContrib.setDisabled(True)
		
		self.EndAction = QtWidgets.QAction("Messung beenden")
		self.EndAction.setShortcut("Ctrl+B")
		self.EndAction.triggered.connect(self.EndMeasure)
		self.EndAction.setDisabled(True)
		
		self.showVariables = QtWidgets.QAction("Variablen anzeigen", self)
		self.showVariables.triggered.connect(self.VariableTable)
		self.showVariables.setDisabled(True)
		
		self.ImportRawFromFile = QtWidgets.QAction("RAW-Datei importieren", self)
		self.ImportRawFromFile.triggered.connect(self.importRaw)
		self.ImportRawFromFile.setShortcut("Ctrl+R")
		self.ImportRawFromFile.setDisabled(True)
		
		menuebar = self.menuBar()
		projectMenue = menuebar.addMenu("Projekt")
		projectMenue.addAction(self.loadProject)
		projectMenue.addAction(self.addContrib)
		projectMenue.addAction(self.showVariables)
		rawMenue = menuebar.addMenu("RAW Daten")
		rawMenue.addAction(self.ImportRawFromFile)
		
		
		#buttons
		self.button_startMeasurement = QtWidgets.QPushButton("Messung starten", self)
		self.button_startMeasurement.adjustSize()
		x = self.button_startMeasurement.size().width() + 20
		y = self.button_startMeasurement.size().height() + 20
		self.button_startMeasurement.resize(x, y)
		x = self.size().width() // 2 - self.button_startMeasurement.size().width() // 2
		y = self.size().height() // 2 - self.button_startMeasurement.size().height() // 2
		self.button_startMeasurement.move(x,y)
		self.button_startMeasurement.setVisible(False)
		
		
		
		self.button_endMeasurement = QtWidgets.QPushButton("Messung beenden", self)
		self.button_endMeasurement.pressed.connect(self.EndMeasure)
		self.button_endMeasurement.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
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
		
		self.LiveValues = ""
		
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
		
		self.manInputFields, self.manInputLabels, self.manInputVarNames = [], [], []
		self.manErrorFields, self.manErrorLabels = [], []
		self.LiveValueMeter, self.LiveValueLabel, self.LiveValueColumns = [], [], []
		self.ArdMeasureCols = []
		
		self.CountdownValue = 0
		
		self.CountDownLabel = QtWidgets.QLabel(self)
		self.CountDownLabel.setFont(self.font_Countdown)
		self.CountDownLabel.setStyleSheet("color: red")
		self.CountDownLabel.setText("5")
		self.CountDownLabel.setVisible(False)
		self.CountDownLabel.adjustSize()
		x = self.size().width() // 2 - self.CountDownLabel.size().width() // 2
		y = self.size().height() // 2 - self.CountDownLabel.size().height() // 2
		self.CountDownLabel.move(x,y)
		
		self.LabelMessungInProgress = QtWidgets.QLabel(self)
		self.LabelMessungInProgress.setText("Messung läuft")
		self.LabelMessungInProgress.setFont(self.font_Bedienelemente)
		self.LabelMessungInProgress.setStyleSheet("color: red")
		self.LabelMessungInProgress.adjustSize()
		self.LabelMessungInProgress.setVisible(False)
		
		
		self.TextArea = QtWidgets.QPlainTextEdit(self)
		self.TextArea.setReadOnly(True)
		self.TextArea.setMinimumSize(300, 300)
		self.TextArea.setMaximumSize(300, 300)
		self.TextArea.move(self.size().width()-350, self.size().height()-350)
		self.TextArea.setPlainText("\u03c9 = 0.42 \n \u00b7")
		self.TextArea.setVisible(False)
		
		self.TableScroll = QtWidgets.QScrollArea(self)
		self.TableScroll.setMinimumSize(300, 300)
		self.Table = QtWidgets.QTableWidget(self.TableScroll)
		self.Table.setMinimumSize(300, 300)
		self.TableScroll.setVisible(False)
		#self.ManualInputButton.setVisible(False)
		
		#print(self.ManualInput1_Label.size().width())
		#self.setMouseTracking(True)
		
		self.inProgress = True
		
		
		

		self.show()
		
			
	def addContribuor(self):
		pass
		
		
	def getProject(self):
		name = QFileDialog.getOpenFileName(self, "Projektdatei wählen", "~/", "XML-Datei (*.xml)")[0]
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
						b = QtWidgets.QPushButton(outputforms[i]["text"], self)
						b.adjustSize()
						b.resize(b.size().width()+8, b.size().height()+8)
						b.move(x, y)
						b.setVisible(False)
						b.clicked.connect(self.getOutput)
						self.buttons_output.append([b, (x,y), i])
						i += 1
				self.showVariables.setDisabled(False)
				self.ImportRawFromFile.setDisabled(False)
			self.step += 1 #is now 1
			self.itemToCalibrate = 0
			self.NumberOfItemsToCalibrate = len(self.Project.calibrationFor(mode="man"))
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
		
			
	
	def getLiveValue(self) -> None:
		print("Yo")
		if self.MeasureMode < 1:
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
			#for i in range(self.number_live_values):
			#	self.LiveValueMeter[i].setText(self.currentArduinoValues[self.LiveValueColumns[i]])
			self.timer.setSingleShot(True)
			self.timer.start(250)
		
		if self.step == 2 and self.MeasureMode > 0:
			self.UpDateLiveMeter()
			if self.Project.control["stop_after"]:
				if self.isRunning:
					if time()-self.startTime > self.Project.control["stop_time"]+0.2:
						self.timer.stop()
						self.EndMeasure()
				else:
					self.startTime = time()
					self.isRunning = True
					if self.Project.ardSleep > 0:
						self.Arduino.readContinously(self.Project.TempFolder, time=self.Project.control["stop_time"], sleep_time=self.Project.ardSleep)
					else:
						self.Arduino.readContinously(self.Project.TempFolder, time=self.Project.control["time"])
			else:
				if not self.isRunning:
					self.isRunning = True
					if self.Project.ardSleep > 0:
						self.Arduino.readContinously(self.Project.TempFolder, sleep_time=self.Project.ardSleep)
					else:
						self.Arduino.readContinously(self.Project.TempFolder)
			
			self.timer.stop()
			self.timer.setSingleShot(False)
			self.timer.start(500)
			
	def saveLiveValue(self):
		if self.step == 1 and self.currentLiveValue != "NIL" and not self.isSet:
				self.Project.setCalibration({"name": self.liveValueVariable, "cvalue": float(self.currentLiveValue)})
				self.itemToCalibrate += 1
				self.isSet = True
	
	def EndMeasure(self):
		self.timer.stop()
		try:
			self.timer.disconnect()
		except:
			pass
		if self.MeasureMode == 1:
			self.ArduinoStopEvent.set()
			loop = QtCore.QEventLoop()					#Warte 500ms, falls Arduino-Klasse gerade schreibt
			QtCore.QTimer.singleShot(500, loop.quit)
			loop.exec_()
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
		vT = True
		self.button_Beenden.setVisible(False)
		self.LabelMessungInProgress.setVisible(False)
		if self.MeasureMode == 1:
			dialog = QtWidgets.QMessageBox()
			dialog.setIcon(QtWidgets.QMessageBox.Information)
			dialog.setText(self.Project.importRAW(self.Arduino.getRawFileName()) + " Werte erfolgreich importiert.")
			dialog.setWindowTitle("Datenimport abgeschlossen")
			dialog.setStandardButtons(QtWidgets.QMessageBox.Ok)
			returnValue = dialog.exec_()
			vT = False
		self.step = 3
		self.Project.MeasurementPostProcessing(valTrans=vT)
		self.OutputMenu()
	
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
				i = 0
				breite = 0
				if self.MeasureMode == 0:
					x_base = 300
				else:
					x_base = 20
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
				
				if self.MeasureMode == 0:
					x = 300
				else:
					x = 20
				if i > self.number_manual_variables or self.MeasureMode != 0:
					self.button_Beenden.move(x, 40+60*i)
				
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
			
			x = 20
			y = self.size().height() - 80
			self.LabelMessungInProgress.move(x, y)
			if self.MeasureMode != 0:
				self.MeasureMode = 1
				self.timer.stop()
				self.CountDownLabel.setVisible(False)
				if self.Project.control["start_countdown"]:
					self.timer.timeout.disconnect()
					self.timer.timeout.connect(self.Countdown)
					self.CountdownValue = self.Project.control["start_delay"]
					self.button_startMeasurement.clicked.connect(self.Countdown)
					self.button_startMeasurement.setVisible(True)
					
				else:
					self.button_startMeasurement.clicked.connect(self.losjetzt)
					self.button_startMeasurement.setVisible(True)
			else:
				self.losjetzt()
	
	def losjetzt(self):
		self.EndAction.setDisabled(False)
		self.button_startMeasurement.setVisible(False)
		self.CountDownLabel.setVisible(False)
		if self.Project.control["stop_button"]:
			self.button_Beenden.setVisible(True)
			self.button_Beenden.setEnabled(True)
			self.button_Beenden.clicked.connect(self.EndMeasure)
		
		#self.button_endMeasurement.setVisible(True)
		
		if self.MeasureMode != 0:
			self.LabelMessungInProgress.setVisible(True)
		self.timer.stop()
		try:
			self.timer.timeout.disconnect()
		except:
			pass
		self.timer.timeout.connect(self.getLiveValue)
		self.timer.setSingleShot(True)
		self.timer.start(10)
		
	def OutputMenu(self):
		for b in self.buttons_output:
			b[0].setVisible(True)
			
	def getOutput(self):
		outputindex = -1
		coming_from = self.sender().pos()
		self.TextArea.setVisible(False)
		self.TableScroll.setVisible(False)
		
		for v in self.buttons_output:
			if coming_from.x() == v[1][0] and coming_from.y() == y[1][1]:
				outputindex = v[1][2]
				break
		if outputindex > -1:
			typ = self.Project.outputs[outputindex]["type"]
			filename = ""
			if typ in ["csv", "xls", "plot"]:
				fil = ("Tabelle speichern", "CSV-Dateien", "csv")
				saveit = True
				if typ == "xls":
					fil = ("Excel-Tabelle speichern", "Excel-Dateien", "xls")
				if typ == "plot":
					fil = ("Plot speichern", "PNG-Bilder", "png")
					saveit = self.Project.outputs[outputindex]["save"]
				if saveit:
					filename, _ = QFileDialog.getSaveFileName(self, fil[0], self.Project.StandardFolder, fil[1] + " (*." + fil[2] + ")")
					try:
						if filename.split(".")[-1].lower() != fil[2]:
							filename = filename + "." + fil[2]
					except:
						filename = filename + "." + fil[2]
				if typ in ["cls", "xls"]:
					self.Project.exportToFile(filename, outputindex)
				else:
					self.plot(filename, outputindex)
			elif typ == "list":
				self.showValuesAsList(outputindex)
			else:
				self.showValuesAsTable(outputindex)
	
	def Countdown(self):
		for i in range(self.number_live_values):
			self.LiveValueMeter[i].setVisible(False)
			self.LiveValueLabel[i].setVisible(False)
			self.button_Beenden.setVisible(False)
		self.CountDownLabel.setVisible(True)
		self.button_startMeasurement.setVisible(False)
		if self.CountdownValue < 0:
			for i in range(self.number_live_values):
				self.LiveValueMeter[i].setVisible(True)
				self.LiveValueLabel[i].setVisible(True)
				self.button_Beenden.setVisible(True)
			self.losjetzt()
		else:
			self.CountDownLabel.setVisible(True)
			self.CountDownLabel.setText(str(self.CountdownValue))
			self.CountdownValue -= 1
			self.timer.setSingleShot(True)
			if self.CountdownValue < 0:
				self.timer.start(100)
			else:
				self.timer.start(1000)
	
	def showText(self, text):
		self.TextArea.setPlainText(text)
		x = self.size().width() - 350
		y = self.size().height() - 350
		self.TextArea.setVisible(True)
		
		
	def showValuesAsList(self, outputindex):
		
		pass
	
	def plot(self, filename, outputindex):
		oinfo = self.Project.outputs[outputindex]
		
		if not matplot_success:
			return
		x_name = oinfo["axis"]["x"]
		y_name = oinfo["axis"]["y"]
		x_unit = self.Project.var_unit(x_name)
		y_unit = self.Project.var_unit(y_name)
		if x_name is None or y_name is None:
			return
		x_values = []
		y_values = []
		if "filter" in self.outputs[outputindex].keys() and len(self.outputs[outputindex]["filter"]) > 0:
			x_values = self.Data.returnValues(x_name, filters=oinfo["filter"])
			y_values = self.Data.returnValues(y_name, filters=oinfo["filter"])
		else:
			x_values = self.Data.returnValues(x_name)
			y_values = self.Data.returnValues(y_name)
		if len(x_values) == 0 or len(y_values) == 0:
			return
		plt.plot(x_values, y_values, oinfo["plotoptions"])
		plt.xlabel(x_name + " [" + x_unit.strip() + "]")
		plt.ylabel(y_name + "[" + y_unit.strip() + "]")
		if "fit" in oinfo.keys():
			fitinfo = self.Project.getfitparam(x_values, y_values, outputindex)
			if fitinfo is not None:
				plt.plot(fitinfo["xfit"], fitinfo["yfit"], oinfo["fit"]["line"])
				if oinfo["fit"]["showparameter"]:
					if oinfo["fit"]["type"] == "poly":
						fittext = self.Project.getFitText(fitinfo, oinfo["fit"]["type"], x_name, y_name, x_unit, y_unit, option=oinfo["fit"]["degree"])
						self.showText(fittext)
				try:
					if "envelop" in oinfo["fit"].keys() and oinfo["fit"]["envelop"] is not None and "envel1" in fitinfo.keys():
						plt.plot(fitinfo["xfit"], fitinfo["envel1"], oinfo["fit"]["envelop"])
						plt.plot(fitinfo["xfit"], fitinfo["envel2"], oinfo["fit"]["envelop"])
				except:
					pass
		if oinfo["save"]:
			plt.savefig(filename, dpi=300)
		plt.show()
		
	def showValuesAsTable(self, outputindex):
		self.Table.setRowCount(100)
		self.Table.setColumnCount(4)
		for i in range(100):
			for j in range(4):
				wi = QtWidgets.QTableWidgetItem(str(i * 4 + j))
				self.Table.setItem(i, j, wi)
		for i in range(4):
			self.Table.resizeColumnToContents(i)
	
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
	
	def importRaw(self):
		name = QFileDialog.getOpenFileName(self, "RAW-Datei wählen", self.Project.StandardFolder, "Arduino Raw (*.raw)")
		self.Project.importRAW(name)
	
	def updateLive(self, v):
		self.LiveValues = v
		
	def getArduino(self):
		p = self.misc.getSerialPorts()
		if len(p) == 1 and self.Project.getBaud() > 0:
			self.Arduino = Arduino.Arduino(p[0][0], self.Project.getBaud(), self.misc, self.ArduinoStopEvent, self)
			self.Arduino.start()

	def UpDateLiveMeter(self):
		canupdate = True
		try:
			livevallist = self.LiveValues.split(self.Project.ardSeperator)
		except:
			canupdate = False
		if canupdate:
			for i in range(self.number_live_values):
				try:
					self.LiveValueMeter[i].setText(livevallist[self.LiveValueColumns[i]])
				except:
					pass
				
app = QtWidgets.QApplication(sys.argv)
ex = GUI()
sys.exit(app.exec_())