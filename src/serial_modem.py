from modem import Modem
import serial

class SerialModem(Modem):

    def __init__(self, port, baud, logger, timeout=5):
        super().__init__(port, baud, logger)
        self.timeout=timeout
        self.logger.info("opening serial modem: {}:{} (timeout: {})".format(self.port, self.baud, self.timeout))
        self.serial=serial.Serial(self.port, self.baud)
        self.serial.timeout=self.timeout
        self.logger.info("serial modem opened: {}:{} (timeout: {})".format(self.port, self.baud, self.timeout))

    def close(self):
        self.logger.info("serial modem closing")
        self.serial.close()
        self.logger.info("serial modem closed")

    def read(self, size):
        self.logger.log("reading from serial modem buffer: {}".format(size))
        return self.serial.read(size)

    def write(self, data):
        self.logger.log("writing to serial modem")
        self.serial.write(data)

