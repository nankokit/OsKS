import time
from collections import deque

import serial
from PySide6.QtCore import QObject, QRunnable, Signal, Slot

import BitStuffing
import PortManager


class SenderSignals(QObject):
    sendedBytes = Signal(int)
    getCollision = Signal(str)
    updateStatus = Signal()
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
                collision = ""
                sended_bit = ""
                bits_sended = 0
                data = self.queue.popleft()
                package = BitStuffing.packaging(data, self.port.port)
                print("sended: " + package)
                package = BitStuffing.bit_stuffing(package)
                print("sended + bitstuffed: " + package)
                try:
                    for bit in package:
                        sended_bit = PortManager.send_bit(self.port, bit)
                        if sended_bit != ("!" * 10):
                            bits_sended += 1
                        if collision:
                            collision += " "
                        collision += sended_bit
                    self.signals.sendedBytes.emit(bits_sended)
                    self.signals.getCollision.emit(collision)
                    self.signals.updateStatus.emit()
                except:
                    self.signals.sendingError.emit()
            else:
                time.sleep(0.01)
