import time

import serial
from PySide6.QtCore import QObject, QRunnable, Signal, Slot

import BitStuffing
import HammingCode
import PortManager


class ReaderSignal(QObject):
    byteReaded = Signal(str)


class SerialReader(QRunnable):
    def __init__(self, port: serial.Serial, *args, **kwargs):
        super().__init__()
        self.port = port
        self.args = args
        self.kwargs = kwargs
        self.signal = ReaderSignal()
        self.running = True

    @Slot()
    def run(self):
        while self.running:
            package = PortManager.get_package(self.port)
            if package and package != "":
                package = BitStuffing.de_bit_stuffing(package)
                data = BitStuffing.depackaging(package)
                data = HammingCode.introduce_random_error(data)
                fcs = HammingCode.get_fcs(package)
                data = HammingCode.validate_and_correct_data(data, fcs)
                self.signal.byteReaded.emit(data)
            time.sleep(0.01)

    def stop(self):
        self.running = False
