import sys
from PyQt5.QtWidgets import QDialog, QApplication
from messung1 import *

class MyMessungQT(QDialog):
    def __init__(self):
        super().__init__()
        self.ui=Ui_Messung()
        self.ui.setupUi(self)
        self.ui.Mstarten.clicked.connect(self.startMessung)
        self.ui.Mstoppen.clicked.connect(self.stopMessung)
        self.show()

    def startMessung(self):
        self.ui.Mstoppen.setEnabled(True)
        self.ui.Mstarten.setEnabled(False)

    def stopMessung(self):
        self.ui.Mstoppen.setEnabled(False)
        self.ui.Mstarten.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MyMessungQT()
    w.show()
    sys.exit(app.exec_())
