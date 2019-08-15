import time

class MessageHandler:
    def __init__(self, logger):
        self.logger=logger

    def handle(self, sms, recipient, message):
        self.logger.info('recipient: {} message: {}'.format(recipient, message))
        if ('test' == message):
            sms.sendSMS(recipient, 'ping pong')
