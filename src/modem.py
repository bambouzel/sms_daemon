from abc import ABC, abstractmethod

# abstract class
class Modem(ABC):
    def __init__(self, port, baud, logger):
        self.port=port
        self.baud=baud
        self.logger=logger

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        return

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def read(self, size):
        pass

    @abstractmethod
    def write(self, data):
        pass