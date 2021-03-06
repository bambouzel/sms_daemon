import os
import sys
import time
import platform
import subprocess

from sms import Sms
from serial_modem import SerialModem
from dummy_modem import DummyModem
from logger import Logger

class Sms_daemon:
    def __init__(self, port, baud, folder, logger, sleep=60):
        self.sms_wrapper=None
        self.port=port
        self.baud=baud
        self.logger=logger
        self.sleep=sleep
        self.home_assistant_beat=0
        self.folder=self.checkFolder(folder)
        self.serviceFolder=self.checkFolder(os.path.join(folder, 'service'))
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
            self.logger.info('creating folder: [{}].'.format(folder))
            os.mkdir(folder)
            os.chmod(folder, 0o777)
        if (not os.path.isdir(folder)):
            self.logger.error('not a directory! [{}].'.format(folder))
            raise ValueError
        elements=sum([len(files) for r, d, files in os.walk(folder)])
        self.logger.info('folder {} contains {} elements.'.format(folder, elements))
        return folder

    def start(self):
        self.logger.info('starting daemon on {}:{} and workspace {}.'.format(self.port, self.baud, self.folder))
        while True:
            try:
                # handle service message
                messages=os.listdir(self.serviceFolder)
                for message in messages:
                    if (os.path.isfile(os.path.join(self.serviceFolder, message))) :
                        self.service(message)

                # heartbeat
                self.hartbeat()

                # check beat of home assistant
                self.checkBeat()

                # handle messages to be sent
                messages=os.listdir(self.sendFolder)
                for message in messages:
                    if (os.path.isfile(os.path.join(self.sendFolder, message))) :
                        self.sendSMS(self.get_sms_wrapper(), message)
                
                # check for incominging messages
                self.get_sms_wrapper().checkSMS(self.receivedFolder)

                # handle service message
                messages=os.listdir(self.serviceFolder)
                for message in messages:
                    if (os.path.isfile(os.path.join(self.serviceFolder, message))) :
                        self.service(message)

                # heartbeat
                self.hartbeat()

                # and go back into loop
                time.sleep(self.sleep)
            except (KeyboardInterrupt):
                exit()

    def get_sms_wrapper(self):
        if (not self.sms_wrapper is None):
            if (self.sms_wrapper.healthy):
                return self.sms_wrapper
            else:
                self.sms_wrapper.close()

        self.sms_wrapper=Sms(DummyModem(self.port, self.baud, self.logger), self.logger)
        return self.sms_wrapper

    def hartbeat(self):
        with open(os.path.join(self.folder, "heartbeat.txt"), 'w') as heartbeat_file:
            if (self.sms_wrapper is None):
                heartbeat_file.write(':'.join([str(time.time()), str(True)]))
            else:
                heartbeat_file.write(':'.join([str(time.time()), str(self.sms_wrapper.healthy)]))

    def sendSMS(self, sms, message):
        os.rename(os.path.join(self.sendFolder, message), os.path.join(self.sendingFolder, message))
        with open(os.path.join(self.sendingFolder, message), 'r') as sms_file:
            data=sms_file.read()
            recipientAndMessage=data.split(':', 1)
            if (len(recipientAndMessage) == 2):
                self.logger.info('sending to {} [{}].'.format(recipientAndMessage[0],recipientAndMessage[1]))
                sms.sendSMS(recipientAndMessage[0],recipientAndMessage[1])
            else:
                self.logger.error('ignoring message: {}'.format(message))
        os.rename(os.path.join(self.sendingFolder, message), os.path.join(self.sentFolder, message))
        return

    def checkBeat(self):
        absolutePath = os.path.join(self.folder, 'home_assistant_beat.txt')
        if (os.path.isfile(absolutePath)):
            self.home_assistant_beat = 0
            os.remove(absolutePath)
        else:
            self.home_assistant_beat = self.home_assistant_beat + 1
            if (self.home_assistant_beat in [5,10,15]):
                self.get_sms_wrapper().sendSMS('+32495640653', 'No running homeassistant found!')

    def service(self, message):
        absolutePath = os.path.join(self.serviceFolder, message)
        with open(absolutePath, 'r') as service_file:
            contents=service_file.read()
            commandAndData=contents.split(':', 1)
            if (len(commandAndData) == 2):
                command = commandAndData[0]
                data = commandAndData[1]
                self.logger.info('service {} [{}].'.format(command,data))
                if (command == 'date'):
                    if (platform.system() == 'Linux'):
                        dateCommand = 'sudo date -s "{}"'.format(data)
                        returnCode = subprocess.call(dateCommand, shell=True)
                        if (returnCode != 0):
                            self.logger.error('could not set date via {}'.format(dateCommand))
                    else:
                        self.logger.error('service command date not supported')
            else:
                self.logger.error('ignoring service: {}'.format(message))
        os.remove(absolutePath)

def main(arguments):
    if (len(arguments) == 3):
        folder=arguments[2]

        heartbeat_file=os.path.join(folder, "heartbeat.txt")
        os.remove(heartbeat_file) if os.path.exists(heartbeat_file) else None
        log_file=os.path.join(folder, "sms_daemon.log")
        os.remove(log_file) if os.path.exists(log_file) else None

        daemon=Sms_daemon(arguments[0], arguments[1], folder, Logger(log_file, Logger.LOG)) 
        daemon.start()
    else:
        print('usage sms_daemon <port> <baud> <folder> <logfile>')

if __name__ == "__main__":
   main(sys.argv[1:])
