import time
from collections import deque

import serial
from PySide6.QtCore import QObject, QRunnable, Signal, Slot

import PortManager


class SenderSignals(QObject):
    sendedBytes = Signal(int)
    collisionInfo = Signal(str)
    writeStats = Signal()
    sendingError = Signal()


class Sender(QRunnable):
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
