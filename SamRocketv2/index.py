import os
import sys
import time
from PyQt5.QtCore import * 
from PyQt5.QtGui import * 
from PyQt5.QtWidgets import * 
from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import Qt
import pandas as pd
from params import codes
from excluded_coloumns import excluded_list

DESKTOP = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') 

class WorkerSignals(QObject):
    progressBar = pyqtSignal(int)

class JobRunner(QRunnable):
    signals = WorkerSignals()
    def __init__(self):
        super().__init__()
        self.is_killed = False

    @pyqtSlot()
    def run(self):
        for n in range(100):
            self.signals.progressBar.emit(n + 1)
            time.sleep(0.1)
            #if self.is_killed:
                #break
    def kill(self):
        self.is_killed = True
    def alive(self):
        self.is_killed = False
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('SamRocketGUI.ui', self)
        #Backgorund Gradient
        p = QPalette()
        gradient = QLinearGradient(0, 700, 0, 0)
        gradient.setColorAt(0.0, QColor(240, 240, 240))
        gradient.setColorAt(1.0, QColor(240, 160, 160))
        p.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(p)
        self.openFiles.clicked.connect(self.open_sheet)
        self.showData.clicked.connect(self.dataHead)
        self.getCSV.clicked.connect(self.pickle)
        self.getHead.clicked.connect(self.getHeader)
        self.getParams.clicked.connect(self.setParams)
        self.getTruncated.clicked.connect(self.removeCol)

        self.threadpool = QThreadPool()
        self.runner = JobRunner()
        self.runner.signals.progressBar.connect(self.update_progress)

        self.show()

    def update_progress(self, n):
        self.progressBar.setValue(n+10)
        if self.runner.is_killed:
            self.progressBar.setValue(100)
            time.sleep(0.1)
            self.progressBar.setValue(0)
            
    def pickle(self):
        path = QFileDialog.getOpenFileName(self, 'Open CSV', os.getenv('HOME'), 'CSV(*.csv)')
        self.all_data = pd.read_csv(path[0], low_memory=False)
        name = path[0].split('/')
        self.all_data.to_pickle(name[-1] + '.pickle')   

    def open_sheet(self):
        path = QFileDialog.getOpenFileName(self, 'Open Pickle', os.getenv('HOME'), 'Pickle (*.pickle)')
        self.all_data = pd.read_pickle(path[0])

    def dataHead(self):
        NumRows = len(self.all_data.index)
        self.tableWidget.setColumnCount(len(self.all_data.columns))
        self.tableWidget.setRowCount(NumRows)
        self.tableWidget.setHorizontalHeaderLabels(self.all_data.columns)
        for i in range(NumRows):
            for j in range(len(self.all_data.columns)):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(self.all_data.iat[i, j])))

        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.resizeRowsToContents()

    def getHeader(self):
        self.all_data = self.all_data.head()

    def setParams(self):
        self.all_data['NaicsCode'] = self.all_data['NaicsCode'].fillna(0).astype(int)
        self.all_data = self.all_data[self.all_data['NaicsCode'].astype(str).isin(codes)]

    def removeCol(self):
        path = QFileDialog.getOpenFileName(self, 'Open CSV', os.getenv('HOME'), 'CSV(*.csv)')
        self.all_data = pd.read_csv(path[0],encoding='cp1252', low_memory=False)
        self.all_data.drop(excluded_list, axis =1, inplace = True)
        name = path[0].split('/')
        self.all_data.to_csv(name[-1] + '-truncated')
  
app = QtWidgets.QApplication(sys.argv) 
window = MainWindow() 
app.exec_() 