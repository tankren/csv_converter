#!/usr/bin/python

import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pandas
import os
from tkinter import filedialog, Tk


class Watcher:
    Tk().withdraw()
    DIRECTORY_TO_WATCH= filedialog.askdirectory()
    
    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
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
                   
if __name__ == '__main__':
    w = Watcher()
    w.run()