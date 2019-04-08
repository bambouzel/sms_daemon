import time

class MessageHandler:
    def __init__(self, logger):
        self.logger=logger

    def handle(self, message):
        self.logger.info('Message: {}'.format(message))
        return
