# -*- coding: utf-8 -*-
# author:rec3wx
 
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pandas
import os
import tkinter as tk
import sys
from datetime import datetime
from PySide6.QtWidgets import *
from PySide6.QtGui import QFont
from PySide6.QtCore import Slot, Qt, QThread, Signal, QEvent
import re
import os
from apscheduler.schedulers.background import BackgroundScheduler

class Watcher:
    DIRECTORY_TO_WATCH= ''
    
    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        try:
            self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=False)
            self.observer.start()
            print ("------------Start monitoring------------")  
            try:
                while True:
                    time.sleep(5)
            except:
                self.observer.stop()
                print("Error")

            self.observer.join()
        except:
            print("Please select the folder to be monitored")


class Handler(FileSystemEventHandler):
    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            try:
                print ("------------New file detected------------")                
                oldfile = event.src_path
                print(oldfile)
                if os.path.splitext(oldfile)[1][1:].strip().lower()== 'csv':
                    filename = os.path.basename(oldfile)
                    path = os.path.dirname(oldfile)
                    newpath = f'{path}\\converted'
                    if not os.path.exists(newpath):
                        os.makedirs(newpath)
                    newfile = f'{path}\\converted\\{filename}'
                    readcsv = pandas.read_csv(oldfile, sep=';', decimal=",")                    
                    print("------------Start converting------------")
                    print(readcsv)
                    readcsv.to_csv(newfile, sep=',', decimal=".", encoding='utf-8')                
                    print("------------Conversion completed------------")
            except Exception as e:
                print(e)    

class Worker(QThread):
    sinOut = Signal(str)
    def __init__(self, parent=None):
        super(Worker, self).__init__(parent)
 
    def run(self):
        pass



class MyWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.thread = Worker()
        title = f'CSV自动转换工具 v0.1   - Made by REC3WX'
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
        self.layout.addWidget((self.text_result), 3, 0, 6, 2)
        self.layout.addWidget((self.btn_reset), 5, 2)
        self.layout.addWidget((self.btn_start), 4, 2)
              
        self.setLayout(self.layout)

        self.thread.sinOut.connect(self.Addmsg)  #解决重复emit

    @Slot()
    def Addmsg(self, message):
        self.text_result.appendPlainText(message)

    def opencsvpath(self):
            csvpath= QFileDialog.getExistingDirectory(self, "选择被监视的CSV文件夹")
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
            self.msgbox('error', '请指定需要监视的文件夹!')
        else:
            pass


    def msgbox(self, title, text):
        tip = QMessageBox(self)
        if title == 'error':
            tip.setIcon(QMessageBox.Critical)
        elif title == 'DONE' :
            tip.setIcon(QMessageBox.Warning)
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