import time
from collections import deque

import serial
from PySide6.QtCore import QObject, QRunnable, Signal, Slot

import PortManager
import BitStuffing


class SenderSignals(QObject):
    sendedBytes = Signal(int)
    collisionInfo = Signal(str)
    writeStats = Signal()
    sendingError = Signal()


class SerialSender(QRunnable):
    def __init__(self, port: serial.Serial, *args, **kwargs):
        super().__init__()
        self.port = port
        self.args = args
        self.kwargs = kwargs
        self.signals = SenderSignals()
        self.running = True
        self.queue = deque()

    def push_data(self, data: str):
        self.queue.append(data)

    def stop(self):
        self.running = False
        self.queue.clear()

    @Slot()
    def run(self):
        while self.running:
            if len(self.queue) != 0:
                package = ""
                collis_info = ""
                collis_info_bit = ""
                bytes_sended = 0
                data = self.queue.popleft()
                package = BitStuffing.packaging(data, self.port.port)
                print("sended: " + package)
                package = BitStuffing.bit_stuffing(package)
                print("sended + bitstuffed: " + package)
                try:
                    for bit in package:
                        collis_info_bit = PortManager.send_byte(self.port, bit)
                        if collis_info_bit != ("!" * 10):
                            bytes_sended += 1
                        if collis_info:
                            collis_info += " "
                        collis_info += collis_info_bit
                    self.signals.sendedBytes.emit(bytes_sended)
                    self.signals.collisionInfo.emit(collis_info)
                    self.signals.writeStats.emit()
                except:
                    self.signals.sendingError.emit()
            else:
                time.sleep(0.01)
