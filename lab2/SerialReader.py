import time

import PortManager
import serial
from PySide6.QtCore import QObject, QRunnable, Signal, Slot


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
            byte = PortManager.PortManager.get_byte(self.port)
            if byte:
                self.signal.byteReaded.emit(byte)
            time.sleep(0.01)

    def stop(self):
        self.running = False
