from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QFileDialog
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
		self.Arduino = None
		
		self.setupUi()
	
	def setupUi(self):
		self.font_bold = QtGui.QFont()
		self.font_bold.setBold(True)
		self.font_Bedienelemente = QtGui.QFont()
		self.font_Bedienelemente.setPointSize(12)
		self.font_LiveWerte = QtGui.QFont()
		self.font_LiveWerte.setPointSize(40)
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
		
		self.buttons_output = []
		
		#self.setMouseTracking(True)
		
		
		

		self.setGeometry(100, 100, 600, 600)
		self.show()
		
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
			self.calibrate()
				#self.buttons_output[1][0].setVisible(True)
				
	def calibrate(self):
		calib_for = self.Project.calibrationFor()
		for c in calib_for:
			self.Label = QtWidgets.QLabel(self)
			self.Label.setText("Kalibriere Variable "+c["name"])
			self.Label.setVisible(True)
			self.Label.setFont(self.font_Bedienelemente)
			self.Label.move(20, 30)
		
		print(calib_for)
		
		
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
		if len(p) == 1 and self.Project.getBaud > 0:
			self.Arduino = Arduino.Arduino(p[0][0], self.Project.getBaud())
			print(self.Arduino.isRunning)

app = QtWidgets.QApplication(sys.argv)
ex = GUI()
sys.exit(app.exec_())