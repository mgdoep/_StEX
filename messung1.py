# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'messung1.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Messung(QtWidgets):


    def setupUi(self, Messung):
        Messung.setObjectName("Messung")
        Messung.setEnabled(True)
        Messung.resize(400, 300)
        Messung.setAutoFillBackground(True)
        self.Mstarten = QtWidgets.QPushButton(Messung)
        self.Mstarten.setGeometry(QtCore.QRect(10, 20, 151, 25))
        self.Mstarten.setObjectName("Mstarten")
        self.Mstoppen = QtWidgets.QPushButton(Messung)
        self.Mstoppen.setEnabled(False)
        self.Mstoppen.setGeometry(QtCore.QRect(10, 60, 151, 25))
        self.Mstoppen.setObjectName("Mstoppen")

        self.retranslateUi(Messung)
        QtCore.QMetaObject.connectSlotsByName(Messung)

    def retranslateUi(self, Messung):
        _translate = QtCore.QCoreApplication.translate
        Messung.setWindowTitle(_translate("Messung", "Messung"))
        self.Mstarten.setText(_translate("Messung", "Messung starten"))
        self.Mstoppen.setText(_translate("Messung", "Messung stoppen"))

