# -*- coding: utf-8 -*-
# author:rec3wx
 
import pandas
import os
import sys
import subprocess
from PySide6.QtWidgets import *
from PySide6.QtGui import QFont
from PySide6.QtCore import Slot, Qt, QThread, Signal, QEvent

    

class Worker(QThread):
    sinOut = Signal(str)

    def __init__(self, parent=None):
        super(Worker, self).__init__(parent)

    def getdata(self, csvpath):
        self.csvpath = csvpath

    def startfile(self, newfolder):
        try:
            os.startfile(newfolder)
        except:
            subprocess.Popen(['xdg-open', newfolder])

    def run(self):
        try:
            file_list = [f for f in os.listdir(self.csvpath) if f.endswith('.csv')]
            if not file_list:
                message = f'没有找到CSV文件! 执行结束!  '
                self.sinOut.emit(message)       
            else: 
                newpath = f'{self.csvpath}\\converted'
                if not os.path.exists(newpath):
                    os.makedirs(newpath)             
                for oldfile in file_list:
                    message = f'开始转换{oldfile}'
                    self.sinOut.emit(message)
                    newfile = f'{newpath}\\{oldfile}'
                    readcsv = pandas.read_csv(f'{self.csvpath}\\{oldfile}', sep=';', decimal=",")
                    readcsv.to_csv(newfile, sep=',', decimal=".", encoding='utf-8')
                    message = f'{oldfile} 转换完成!!  '
                    self.sinOut.emit(message)
                message = '全部转换完成, 打开转换结果文件夹'
                self.sinOut.emit(message)
                self.startfile(newpath)
        except Exception as e:
            message = f'{e}'
            self.sinOut.emit(message)      


class MyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread = Worker()
        title = f'CSV批量转换工具 v0.2   - Made by REC3WX'
        self.setWindowTitle(title)
        pixmapi = QStyle.SP_FileDialogDetailedView
        icon = self.style().standardIcon(pixmapi)
        self.setWindowIcon(icon)
        self.setFixedSize(700, 300)
        
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(icon)
        self.tray.setToolTip(f'{title} 正在后台运行')
        self.tray.activated.connect(self.on_systemTrayIcon_activated)
        
        self.fld_csv = QLabel('CSV文件夹:')
        self.btn_csv = QPushButton('打开')
        self.btn_csv.clicked.connect(self.opencsvpath)
        self.line_csv = QLineEdit()
        self.line_csv.setClearButtonEnabled(True)

        self.btn_start = QPushButton('执行')
        self.btn_start.clicked.connect(self.execute)

        self.fld_sch = QLabel('定时任务时间:')
        self.time_sch = QTimeEdit()
        self.time_sch.setDisplayFormat("HH:mm")
        self.time_sch.setCursor(Qt.PointingHandCursor)
             
        self.fld_result = QLabel('运行日志:')
        self.text_result = QPlainTextEdit()
        self.text_result.setReadOnly(True)
       
        self.btn_reset = QPushButton('清空日志')
        self.btn_reset.clicked.connect(self.reset_log)

        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.line.setFrameShadow(QFrame.Sunken)

        self.layout = QGridLayout()
        self.layout.addWidget((self.fld_csv), 0, 0)
        self.layout.addWidget((self.line_csv), 0, 1)
        self.layout.addWidget((self.btn_csv), 0, 2)        

        self.layout.addWidget((self.line), 1, 0, 1, 3)
        self.layout.addWidget((self.fld_result), 2, 0)
        self.layout.addWidget((self.text_result), 3, 0, 4, 2)
        self.layout.addWidget((self.btn_reset), 5, 2)
        self.layout.addWidget((self.btn_start), 4, 2)
              
        self.setLayout(self.layout)

        self.thread.sinOut.connect(self.addmsg)  #解决重复emit

    @Slot()
    def addmsg(self, message):
        self.text_result.appendPlainText(message)

    def opencsvpath(self):
        desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        csvpath= QFileDialog.getExistingDirectory(self, "选择CSV文件夹", desktop, QFileDialog.ShowDirsOnly)
        self.line_csv.setText(csvpath)

    def on_systemTrayIcon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isHidden():
                self.show()
                self.activateWindow()
                self.tray.hide()
                
    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if self.windowState() & Qt.WindowMinimized:
                event.ignore()
                self.hide()
                self.tray.show()
                
    def closeEvent(self, event):
        result = QMessageBox.question(self, "警告", "是否确认退出? ", QMessageBox.Yes | QMessageBox.No)
        if(result == QMessageBox.Yes):
            event.accept()
        else:
            event.ignore()

    def reset_log(self):
        confirm = QMessageBox.question(self, "警告", "是否清空日志? ", QMessageBox.Yes | QMessageBox.No)
        if(confirm == QMessageBox.Yes):
            self.text_result.clear()

    def execute(self):
        if self.line_csv.text() == "":
            self.msgbox('error', '请指定CSV文件夹!')
        else:
            self.addmsg(f'开始执行批量转换, 目标文件夹{self.line_csv.text()}')
            csvpath = self.line_csv.text() 
            self.thread.getdata(csvpath)
            self.thread.start()

    def msgbox(self, title, text):
        tip = QMessageBox(self)
        if title == 'error':
            tip.setIcon(QMessageBox.Critical)
        elif title == 'warn':
            tip.setIcon(QMessageBox.Warning)
        elif title == 'info':
            tip.setIcon(QMessageBox.information)
        tip.setWindowFlag(Qt.FramelessWindowHint)
        font = QFont()
        font.setFamily("Microsoft YaHei")
        font.setPointSize(9)
        tip.setFont(font)
        tip.setText(text)
        tip.exec()                                  

def main():
    if not QApplication.instance():
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
    font = QFont()
    font.setFamily("Microsoft YaHei")
    font.setPointSize(10)
    app.setFont(font)
    widget = MyWidget()
    #app.setStyleSheet(qdarktheme.load_stylesheet(border="rounded"))
    app.setStyle("fusion")
    
    widget.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()        