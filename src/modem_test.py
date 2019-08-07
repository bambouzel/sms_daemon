import os
import sys
import time
import serial
from serial_modem import SerialModem
from logger import Logger

def main(arguments):
    if (len(arguments) == 2):
        print('modem_test {} {}'.format(arguments[0], arguments[1]))
        modem=serial.Serial(arguments[0], arguments[1], timeout=1)
        modem.write("AT".encode() + b'\r')
        time.sleep(1)
        print("received: {}".format(modem.read(200).decode("utf-8")))
        modem.close()

        log_file=os.path.join(".", "modem_test.log")
        another=SerialModem(arguments[0], arguments[1], Logger(log_file, Logger.LOG), 1)
        another.write("AT".encode() + b'\r')
        time.sleep(1)
        print("received: {}".format(another.read(200).decode("utf-8")))
        another.close()
    else:
        print('usage modem_test <port> <baud>')

if __name__ == "__main__":
   main(sys.argv[1:])
