import sys
import time

from message_handler import MessageHandler
from dummy_modem import DummyModem
#import serial

class Sms:
    def __init__(self, port, baud, logger):
        self.modem=None
        self.port=port
        self.baud=baud
        self.logger=logger
        #self.modem=serial.Serial(self.port, self.baud, timeout=5)
        self.modem=DummyModem(logger, self.port, self.baud, timeout=5)
        self.messageHandler=MessageHandler(logger)
        self.need_to_register = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.modem.close()
        return

    def sendSMS(self, recipient, message):
        self.logger.info('Sending SMS to {} ({})'.format(recipient, message))
        if (self.waitForNetwork()):
            return self.sendSMSonNetwork(recipient, message)
        return False

    def checkSMS(self):
        if (self.waitForNetwork()):
            if "OK" in self.send("AT+CMGF=1"):
                # set message store to SM
                if "OK" in self.waitForResponse("AT+CPMS=?"):
                    if "OK" in self.send("AT+CPMS=\"SM\",\"SM\",\"SM\""):
                        # retrieve all messages
                        messages = self.waitForResponse("AT+CMGL=\"ALL\"")
                        if "OK" in messages:
                            return self.handleMessages(messages)
        self.need_to_register = False
        return False

    def handleMessages(self, messages):
        messageList=messages.split("+CMGL:")
        for message in messageList:
            parts=message.split(",")
            if (len(parts)>=6):
                self.handleMessage(parts[0])
        return True

    def handleMessage(self, index):
        trimmed=index.strip()
        self.logger.log('Read message: {}'.format(trimmed))
        message=self.waitForResponse("AT+CMGR="+trimmed)
        if "OK" in message:
            parts=message.split(",")
            if (len(parts)>=5):
                self.handleData(message)
                if "OK" in self.send("AT+CMGD="+trimmed):
                    self.logger.log('Delete message: {}'.format(trimmed))
                    return True
            else:
                return True
        self.need_to_register = False
        return False

    def handleData(self, message):
        # get data between last quotes and "OK" and strip it
        lastQuotes=message.rfind('"')
        if (lastQuotes>0):
            ok=message.rfind('OK')
            if (ok>lastQuotes):
                self.messageHandler.handle(message[lastQuotes+1:ok].strip())
        return

    def send(self, command):
        self.logger.log('Sending: {}'.format(command))
        self.modem.write(command.encode() + b'\r')
        time.sleep(1)
        response=self.modem.read(200)
        answer=response.decode("utf-8")
        self.logger.log('Received: {}'.format(answer))
        return answer

    def waitForResponse(self, command):
        self.logger.log('Sending: {}'.format(command))
        self.modem.write(command.encode() + b'\r')
        time.sleep(1)
        response=self.read_bytes(self.modem)
        answer=response.decode("utf-8")
        self.logger.log('Received: {}'.format(answer))
        return answer

    # read all bytes on the serial port and return them
    def read_bytes(self, port, buffer_size=20):
        if not port.timeout:
            raise TypeError('Port needs to have a timeout set!')

        read_buffer=b''
        while True:
            bytes_read=port.read(size=buffer_size)
            read_buffer+=bytes_read
			# stop if less data is read then the buffer_size
            if (not len(bytes_read) == buffer_size):
                break

        return read_buffer

    def waitForNetwork(self):
        if (not self.need_to_register):
            self.logger.log('Registering on: {}'.format(self.modem.portstr)) 

            # attention
            if "OK" not in self.send("AT"):
                return False
            # no echo
            if "OK" not in self.send("ATE0"):
                return False
            # verbose error log
            if "OK" not in self.send("AT+CMEE=2"):
                return False
            #
            # enter SIM PIN to register on network
            #
            if "READY" not in self.send("AT+CPIN?"):
                self.send("AT+CPIN=1111")
                if "READY" not in self.send("AT+CPIN?"):
                    return False

            #self.send("AT+CREG?")	# registered to network?
            #self.send("AT+COPS?")	# registered to which network
            #self.send("AT+CSQ=?")	# signal quality
            #self.send("AT+CSQ")	# signal quality

            self.need_to_register = True
            return True

    def sendSMSonNetwork(self, recipient, message):
        if "OK" in self.send("AT+CMGF=1"):
            if ">" in self.send("AT+CMGS=\"" + recipient + "\""):
                self.send(message)
                self.modem.write(bytes([26]))
                return True
        self.need_to_register = False
        return False
