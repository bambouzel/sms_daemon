import os
import sys
import time

from message_handler import MessageHandler

class Sms:
    def __init__(self, modem, logger):
        self.modem=modem
        self.healthy=False
        self.logger=logger
        self.messageHandler=MessageHandler(logger)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return

    def close(self):
        self.modem.close()

    def sendSMS(self, recipient, message):
        self.logger.info('sending SMS to {} ({})'.format(recipient, message))
        if (self.waitForNetwork()):
            return self.sendSMSonNetwork(recipient, message)
        return False

    def checkSMS(self, receivedFolder):
        if (self.waitForNetwork()):
            if "OK" in self.send("AT+CMGF=1"):
                # set message store to SM
                if "OK" in self.waitForResponse("AT+CPMS=?"):
                    if "OK" in self.send("AT+CPMS=\"SM\",\"SM\",\"SM\""):
                        # first delete all read and sent messages
                        if "OK" in self.send("AT+CMGD=1,3"):
                            # retrieve all messages
                            messages = self.waitForResponse("AT+CMGL=\"ALL\"")
                            if "OK" in messages:
                                if (self.handleMessages(messages, receivedFolder)):
                                    return True
        self.healthy=False
        return False

    def handleMessages(self, messages, receivedFolder):
        messageList=messages.split("+CMGL:")
        for message in messageList:
            parts=message.split(",")
            if (len(parts)>=6):
                if (not self.handleMessage(parts[0], receivedFolder)):
                    return False
        return True

    def handleMessage(self, index, receivedFolder):
        trimmed=index.strip()
        self.logger.log('read message: {}'.format(trimmed))
        message=self.waitForResponse("AT+CMGR="+trimmed)
        if "OK" in message:
            parts=message.split(",")
            if (len(parts)>=5):
                self.handleData(message)
                with open(os.path.join(receivedFolder, str(time.time()) + ".log"), 'a+') as msg_file:
                    msg_file.write(message + "\n")
                # message will be deleted in a next run (read message)
            else:
                self.logger.info('ignoring message: {}:{}'.format(trimmed, message))
            return True
        return False

    def handleData(self, message):
        # get data between quotes 3 and 4 -> recipient
        recipient=self.getQuoted(message, 2)
        # get data between last quotes and "OK" and strip it
        lastQuotes=message.rfind('"')
        if (lastQuotes>0):
            ok=message.rfind('OK')
            if (ok>lastQuotes):
                self.messageHandler.handle(self, recipient, message[lastQuotes+1:ok].strip())

    def getQuoted(self, message, index):
        i=1
        start=0
        while i<=index:
            start=message.find("\"", start)
            if (start==-1):
                return None
            end=message.find("\"", start+1)
            if (end==-1):
                return None
            if (i==index):
                return message[start+1:end]
            start=end+1
            i=i+1
        return None

    def send(self, command):
        self.logger.log('sending: {}'.format(command))
        self.modem.write(command.encode() + b'\r')
        time.sleep(1)
        response=self.modem.read(200)
        answer=response.decode("utf-8")
        self.logger.log('received: {}'.format(answer))
        return answer

    def waitForResponse(self, command):
        self.logger.log('sending: {}'.format(command))
        self.modem.write(command.encode() + b'\r')
        time.sleep(1)
        response=self.read_bytes(self.modem)
        answer=response.decode("utf-8")
        self.logger.log('received: {}'.format(answer))
        return answer

    # read all bytes on the serial port and return them
    def read_bytes(self, serialPort, buffer_size=20):
        if not serialPort.timeout:
            raise TypeError('serial ports needs to have a timeout set!')

        read_buffer=b''
        while True:
            bytes_read=serialPort.read(size=buffer_size)
            read_buffer+=bytes_read
			# stop if less data is read then the buffer_size
            if (not len(bytes_read) == buffer_size):
                break

        return read_buffer

    def waitForNetwork(self):
        if (self.healthy):
            return True

        self.logger.log('registering on: {}:{}'.format(self.modem.port, self.modem.baud)) 

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

        self.healthy=True
        return self.healthy

    def sendSMSonNetwork(self, recipient, message):
        if "OK" in self.send("AT+CMGF=1"):
            if ">" in self.send("AT+CMGS=\"" + recipient + "\""):
                self.send(message)
                self.modem.write(bytes([26]))
                return True
        self.healthy=False
        return False