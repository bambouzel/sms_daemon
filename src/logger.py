import os
import time

class Logger:
    def __init__(self, directory, logfile, type):
        self.directory=directory
        self.logfile=logfile
        self.type=type

    def log(self, message):
        now = time.strftime("%d/%m/%Y %H:%M:%S")
        line='[{}] {}\n'.format(now, message)
        if (self.type==2):
            self.write(line)
        elif (self.type==1):
            print(line)

    def error(self, message):
        now = time.strftime("%d/%m/%Y %H:%M:%S")
        self.write('[{}] {}\n'.format(now, message))

    def info(self, message):
        now = time.strftime("%d/%m/%Y %H:%M:%S")
        self.write('[{}] {}\n'.format(now, message))
    
    def write(self, message):
        if os.path.exists(self.directory):
            with open(os.path.join(self.directory, self.logfile), "a") as handle:
                handle.write(message)
        else:
            print(message)