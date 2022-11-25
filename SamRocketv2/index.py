import os
import sys
import time
import sysinfo
from PyQt5.QtCore import * 
from PyQt5.QtGui import * 
from PyQt5.QtWidgets import * 
from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5 import QtCore
import pandas as pd
from params import codes
from excluded_coloumns import excluded_list

DESKTOP = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop') 

class WorkerSignals(QObject):
    progress = pyqtSignal(int)

class JobRunner(QRunnable):
    signals = WorkerSignals()
    def __init__(self):
        super().__init__()

    @pyqtSlot()
    def run(self):
        while 1:
            val = sysinfo.getCPU()
            self.signals.progress.emit(val)
            time.sleep(5)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('SamRocketGUI.ui', self)
        #Backgorund Gradient
        p = QPalette()
        gradient = QLinearGradient(0, 700, 0, 0)
        gradient.setColorAt(0.0, QColor(240, 240, 240))
        gradient.setColorAt(1.0, QColor(240, 160, 160))
        p.setBrush(QPalette.Window,  QBrush(gradient))
        self.setPalette(p)
        self.progressBar.setFormat('    CPU Usage: %p%' )
        self.openFiles.clicked.connect(self.open_sheet)
        self.showData.clicked.connect(self.dataHead)
        self.getCSV.clicked.connect(self.pickle)
        self.getHead.clicked.connect(self.getHeader)
        self.getParams.clicked.connect(self.setParams)
        self.getTruncated.clicked.connect(self.removeCol)
        
        self.threadpool = QThreadPool()
        self.runner = JobRunner()
        self.runner.signals.progress.connect(self.update_progress)
        self.threadpool.start(self.runner)

        self.show()

    def update_progress(self):
        val = sysinfo.getCPU()
        self.progressBar.setValue(int(val))
            
    def pickle(self):
        try:
            path = QFileDialog.getOpenFileName(self, 'Open CSV', os.getenv('HOME'), 'CSV(*.csv)')
            self.all_data = pd.read_csv(path[0],encoding='cp1252', low_memory=False)
            name = path[0].split('/')
            self.all_data.to_pickle(name[-1] + '.pickle')
        except Exception as e:
            self.sendError(e)
            path = QFileDialog.getOpenFileName(self, 'Open CSV', os.getenv('HOME'), 'CSV(*.csv)')
            self.all_data = pd.read_csv(path[0],encoding='cp1252', low_memory=False)
            name = path[0].split('/')
            self.all_data.to_pickle(name[-1] + '.pickle')

    def open_sheet(self):
        try:
            path = QFileDialog.getOpenFileName(self, 'Open Pickle', os.getenv('HOME'), 'Pickle (*.pickle)')
            self.all_data = pd.read_pickle(path[0])
        except Exception as e:
            self.sendError(e)
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
        try:
            path = QFileDialog.getOpenFileName(self, 'Open CSV', os.getenv('HOME'), 'Pickle (*.pickle)')
            self.all_data = pd.read_pickle(path[0])
            self.all_data.drop(excluded_list, axis =1, inplace = True)
            name = path[0].split('/')
            self.all_data.to_csv(name[-1] + '-truncated')
        except Exception as e:
            self.sendError(e)
            path = QFileDialog.getOpenFileName(self, 'Open CSV', os.getenv('HOME'), 'Pickle (*.pickle)')
            self.all_data = pd.read_pickle(path[0])
            self.all_data.drop(excluded_list, axis =1, inplace = True)
            name = path[0].split('/')
            self.all_data.to_csv(name[-1] + '-truncated')

    def sendError(self, e):
        self.msg = QMessageBox()
        self.msg.setWindowTitle("Error!")
        self.msg.setIcon(QMessageBox.Critical)
        self.msg.setText("Please Select File!")
        self.msg.setDetailedText(str(e))
        self.msg.setStandardButtons(QMessageBox.Retry)
        self.msg.exec_()
app = QtWidgets.QApplication(sys.argv) 
window = MainWindow() 
app.exec_() 