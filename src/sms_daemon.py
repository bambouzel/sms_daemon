import os
import sys
import time

from sms import Sms
from logger import Logger

class Sms_daemon:
    def __init__(self, port, baud, folder, logger):
        self.port=port
        self.baud=baud
        self.logger=logger
        self.folder=self.checkFolder(folder)
        self.sendFolder=self.checkFolder(os.path.join(folder, 'send'))
        self.sendingFolder=self.checkFolder(os.path.join(folder, 'sending'))
        self.sentFolder=self.checkFolder(os.path.join(folder, 'sent'))
        self.receivedFolder=self.checkFolder(os.path.join(folder, 'received'))
        self.recover()

    def recover(self):
        sending=os.listdir(self.sendingFolder)
        for message in sending:
            if (os.path.isfile(os.path.join(self.sendingFolder, message))) :
                os.rename(os.path.join(self.sendingFolder, message), os.path.join(self.sendFolder, message))
        return

    def checkFolder(self, folder):
        if (not os.path.exists(folder)):
            self.logger.info('Creating folder: [{}].'.format(folder))
            os.mkdir(folder)
            os.chmod(folder, 0o777)
        if (not os.path.isdir(folder)):
            self.logger.error('Not a directory! [{}].'.format(folder))
            raise ValueError
        elements=sum([len(files) for r, d, files in os.walk(folder)])
        self.logger.info('Folder {} contains {} elements.'.format(folder, elements))
        return folder

    def start(self):
        self.logger.info('Starting daemon on {}:{} and workspace {}.'.format(self.port, self.baud, self.folder))
        with Sms(self.port, self.baud, self.logger) as self.sms:
            while True:
                try:
                    # handle messages to be sent
                    messages=os.listdir(self.sendFolder)
                    for message in messages:
                        if (os.path.isfile(os.path.join(self.sendFolder, message))) :
                            self.sendSMS(message)
                    
                    # check for incominging messages
                    self.checkSMS()

                    # and go back into loop
                    time.sleep(1)
                except (KeyboardInterrupt):
                    exit()

    def sendSMS(self, message) :
        os.rename(os.path.join(self.sendFolder, message), os.path.join(self.sendingFolder, message))
        with open(os.path.join(self.sendingFolder, message), 'r') as sms_file:
            data=sms_file.read().replace('\n', '')
            recipientAndMessage=data.split(':', 1)
            if (len(recipientAndMessage) == 2):
                self.logger.log('Sending to {} [{}].'.format(recipientAndMessage[0],recipientAndMessage[1]))
                self.sms.sendSMS(recipientAndMessage[0],recipientAndMessage[1])
            else:
                self.logger.error('Ignoring message: {}'.format(message))
        os.rename(os.path.join(self.sendingFolder, message), os.path.join(self.sentFolder, message))
        return

    def checkSMS(self) :
        with Sms(self.port, self.baud, self.logger) as sms:
            sms.checkSMS()
        return

def main(arguments):
    if (len(arguments) == 4):
        with open(arguments[3], "a") as logfile:
            daemon=Sms_daemon(arguments[0], arguments[1], arguments[2], Logger(logfile, 0)) 
            daemon.start()
    else:
        print('Usage sms_daemon <port> <baud> <folder> <logfile>')

if __name__ == "__main__":
   main(sys.argv[1:])