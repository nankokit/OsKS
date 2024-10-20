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
                package = BitStuffing.depackaging(package)
                package = HammingCode.distort_data(package)
                package = HammingCode.check_and_correct(
                    package, HammingCode.fcs_from_package(package)
                )
                self.signal.byteReaded.emit(package)
            time.sleep(0.01)

    def stop(self):
        self.running = False
