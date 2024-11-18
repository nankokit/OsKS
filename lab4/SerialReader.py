import time

import serial
from PySide6.QtCore import QObject, QRunnable, Signal, Slot

import BitStuffing
import constants
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
        package = ""
        flag = False
        while self.running:
            data = PortManager.get_byte(self.port)
            if data == "j":
                package = package[:-1]
                print("readed:" + package)
            elif data:
                package += data
                print("readed:" + package)
                if not flag:
                    if package == constants.FLAG:
                        flag = True
                elif flag:
                    if (
                        package[len(constants.FLAG) :][-len(constants.FLAG) :]
                        == constants.FLAG
                    ):
                        package = BitStuffing.de_bit_stuffing(package)
                        if PortManager.full_packet(package):
                            data = BitStuffing.depackaging(package)
                            data = HammingCode.introduce_random_error(data)
                            fcs = HammingCode.get_fcs(package)
                            data = HammingCode.validate_and_correct_data(data, fcs)
                            self.signal.byteReaded.emit(data)
                        package = constants.FLAG
            else:
                if flag:
                    package = BitStuffing.de_bit_stuffing(package)
                    if PortManager.full_packet(package):
                        data = BitStuffing.depackaging(package)
                        data = HammingCode.introduce_random_error(data)
                        fcs = HammingCode.get_fcs(package)
                        data = HammingCode.validate_and_correct_data(data, fcs)
                    self.signal.byteReaded.emit(data)
                    flag = False
                    package = ""
            time.sleep(0.01)

    def stop(self):
        self.running = False
