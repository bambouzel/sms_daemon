import time

class Logger:
    def __init__(self, logfile, type):
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
        with open(self.logfile, "a") as handle:
            handle.write(message)