import time

import serial
from PySide6.QtCore import QObject, QRunnable, Signal, Slot

import BitStuffing
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
        self.package = ""

    @Slot()
    def run(self):
        while self.running:
            byte = PortManager.get_package(self.port)
            if byte and byte != "":
                self.package += byte
            elif len(self.package) != 0:
                self.signal.byteReaded.emit(BitStuffing.de_bit_stuffing(self.package))
                self.package = ""
            time.sleep(0.01)

    def stop(self):
        self.running = False
