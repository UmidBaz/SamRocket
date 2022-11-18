from PyQt5.QtCore import * 
from PyQt5.QtGui import * 
from PyQt5.QtWidgets import * 
import sys
from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import Qt

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('SamRocketGUI.ui', self)
        #Backgorund Gradient
        p = QPalette()
        gradient = QLinearGradient(0, 1000, 0, 0)
        gradient.setColorAt(0.0, QColor(240, 240, 240))
        gradient.setColorAt(1.0, QColor(240, 160, 160))
        p.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(p)
        self.show()


app = QtWidgets.QApplication(sys.argv) 
window = MainWindow() 
app.exec_() 