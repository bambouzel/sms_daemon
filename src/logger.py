import time

class Logger:
    def __init__(self, logfile, type):
        self.logfile=logfile
        self.type=type

    def log(self, message):
        now = time.strftime("%d/%m/%Y %H:%M:%S")
        line='[{}] {}\n'.format(now, message)
        if (self.type==2):
            self.logfile.write(line)
            self.logfile.flush()
        elif (self.type==1):
            print(line)

    def error(self, message):
        now = time.strftime("%d/%m/%Y %H:%M:%S")
        self.logfile.write('[{}] {}\n'.format(now, message))
        self.logfile.flush()

    def info(self, message):
        now = time.strftime("%d/%m/%Y %H:%M:%S")
        self.logfile.write('[{}] {}\n'.format(now, message))
        self.logfile.flush()
