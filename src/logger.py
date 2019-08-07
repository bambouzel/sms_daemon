import os
import time

class Logger:

    NONE='none'
    INFO='info'
    LOG='log'

    def __init__(self, logfile, type, print=False):
        self.logfile=logfile
        self.type=type
        self.print=print

    def log(self, message):
        now = time.strftime("%d/%m/%Y %H:%M:%S")
        line='[{}] {}\n'.format(now, message)
        if (self.type==self.LOG):
            self.write(line)

    def error(self, message):
        now = time.strftime("%d/%m/%Y %H:%M:%S")
        self.write('[{}] {}\n'.format(now, message))

    def info(self, message):
        now = time.strftime("%d/%m/%Y %H:%M:%S")
        if (self.type==self.INFO or self.type==self.LOG):
            self.write('[{}] {}\n'.format(now, message))
    
    def write(self, message):
        if (self.print):
            print(message)
        with open(self.logfile, "a") as handle:
            handle.write(message)