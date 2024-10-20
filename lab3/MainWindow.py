import sys

import serial
from PySide6.QtCore import Qt, QThreadPool, QTimer
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import BitStuffing
import constants
import PortManager
import SerialReader
from CustomTextEdit import AppendOnlyTextEdit


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("COM-port communication 2")
        self.setGeometry(100, 100, 800, 500)

        # Инициализация логики последовательных портов
        self.write_port = serial.Serial()
        self.read_port = serial.Serial()
        self.thread_pool = QThreadPool()
        self.port_reader = SerialReader.SerialReader(self.read_port)
        self.bytes_sended = 0
        self.data = ""
        self.last_package = ""

        # Установка основного виджета
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Ввод данных
        input_layout = QVBoxLayout()
        com1_layout = QHBoxLayout()
        com1_layout.addWidget(QLabel("Sending COM-port:"))
        self.sending_combo = QComboBox()
        com1_layout.addWidget(self.sending_combo)
        input_layout.addLayout(com1_layout)

        input_label = QLabel("Data for sending:")
        self.input_text = AppendOnlyTextEdit()
        self.input_text.setPlaceholderText("Write a message...")
        input_layout.addWidget(input_label)
        input_layout.addWidget(self.input_text)

        clear_input_button = QPushButton("Clear sending section")
        clear_input_button.clicked.connect(self.clear_input)
        input_layout.addWidget(clear_input_button)

        main_layout.addLayout(input_layout)

        # Вывод данных
        output_layout = QVBoxLayout()
        com2_layout = QHBoxLayout()
        com2_layout.addWidget(QLabel("Receiving COM-port:"))
        self.receiving_combo = QComboBox()
        com2_layout.addWidget(self.receiving_combo)
        output_layout.addLayout(com2_layout)

        output_label = QLabel("Received data:")
        self.output_text = QPlainTextEdit()
        self.output_text.setReadOnly(True)
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_text)

        clear_output_button = QPushButton("Clear received section")
        clear_output_button.clicked.connect(self.clear_output)
        output_layout.addWidget(clear_output_button)

        main_layout.addLayout(output_layout)

        # Информация о состоянии
        info_layout = QVBoxLayout()

        # Кнопка для обновления информации о портах
        update_ports_button = QPushButton("Update ports info")
        update_ports_button.clicked.connect(self.update_ports)
        info_layout.addWidget(update_ports_button)

        status_label = QLabel("STATUS")
        info_layout.addWidget(status_label)

        self.status_text = QPlainTextEdit()
        self.status_text.setReadOnly(True)
        info_layout.addWidget(self.status_text)

        log_label = QLabel("DEBUG")
        info_layout.addWidget(log_label)
        self.debug_text = QPlainTextEdit()
        self.debug_text.setReadOnly(True)
        info_layout.addWidget(self.debug_text)

        main_layout.addLayout(info_layout)

        # Установка коэффициентов растяжения
        main_layout.setStretch(0, 1)  # Input column
        main_layout.setStretch(1, 1)  # Output column
        main_layout.setStretch(2, 1)  # Info column

        # Подключение сигналов
        self.sending_combo.currentTextChanged.connect(self.change_sending_port)
        self.receiving_combo.currentTextChanged.connect(self.change_received_port)
        self.input_text.realTextEdited.connect(self.send_package)

        # Таймер для обновления состояния
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1000)

        self.update_ports()

    def set_box_list(self, comboBox: QComboBox, without: list):
        ports_list = PortManager.get_all_ports()
        text = comboBox.currentText()
        if text != "":
            ports_list.append(text)
        for port in without:
            try:
                ports_list.remove(port)
            except ValueError:
                pass
        ports_list.sort()
        was_blocked = comboBox.blockSignals(True)
        comboBox.clear()
        comboBox.addItems(ports_list)
        comboBox.setCurrentText(text)
        if text == "":
            comboBox.setCurrentIndex(-1)
        comboBox.blockSignals(was_blocked)

    def update_ports(self):
        text_write = self.receiving_combo.currentText()

        # Убираем выбранный и следующий порты из списка получения
        self.set_box_list(
            self.receiving_combo,
            [
                self.sending_combo.currentText(),
                self.get_next_port(self.sending_combo.currentText()),
            ],
        )

        # Убираем выбранный и предыдущий порты из списка отправки
        self.set_box_list(
            self.sending_combo,
            [
                self.receiving_combo.currentText(),
                self.get_previous_port(self.receiving_combo.currentText()),
            ],
        )

        if text_write == "":
            self.input_text.setEnabled(False)
            self.input_text.set_text("Select port")

    def get_next_port(self, port):
        if port:
            return port[:-1] + str(int(port[-1]) + 1)
        return ""

    def get_previous_port(self, port):
        if port:
            return port[:-1] + str(int(port[-1]) - 1)
        return ""

    def show_error_message(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Error")
        msg.setInformativeText(message)
        msg.setWindowTitle("Error")
        msg.exec()

    def change_received_port(self, port: str):
        self.port_reader.stop()
        self.thread_pool.clear()
        self.read_port.close()
        self.clear_output()

        self.bytes_sended = 0

        if PortManager.connect_to_port(port).port is None:
            self.show_error_message(
                "The port is already occupied, the list of ports has been updated"
            )
            was_blocked = self.receiving_combo.blockSignals(True)
            self.receiving_combo.setCurrentIndex(-1)
            self.update_ports()
            self.receiving_combo.blockSignals(was_blocked)
            return

        self.read_port = PortManager.connect_to_port(port)
        self.port_reader = SerialReader.SerialReader(self.read_port)
        self.port_reader.signal.byteReaded.connect(self.write_text)
        self.thread_pool.start(self.port_reader)

        self.log(f"Connected to receiving port: {port}")
        self.update_ports()
        self.update_status()

        # Убираем надпись "Select port" если порты открыты
        self.check_ports_status()

    def change_sending_port(self, port: str):
        self.clear_input()
        self.write_port.close()

        if PortManager.connect_to_port(port).port is None:
            self.show_error_message(
                "The port is already occupied, the list of ports has been updated"
            )
            was_blocked = self.sending_combo.blockSignals(True)
            self.sending_combo.setCurrentIndex(-1)

            self.input_text.setEnabled(False)
            self.input_text.set_text("Select port")
            self.update_ports()
            self.sending_combo.blockSignals(was_blocked)
            return

        self.input_text.setEnabled(True)
        self.write_port = PortManager.connect_to_port(port)
        self.write_port.write_timeout = 0.1

        self.log(f"Connected to sending port: {port}")
        self.update_ports()
        self.update_status()

        # Убираем надпись "Select port" если порты открыты
        self.check_ports_status()

    def check_ports_status(self):
        if self.write_port.is_open:
            self.input_text.setEnabled(True)
            self.input_text.set_text("")
        else:
            self.input_text.setEnabled(False)
            self.input_text.set_text("Select port")

    def send_package(self):
        if self.write_port.is_open and self.input_text.toPlainText():
            self.data += self.input_text.toPlainText()[-1]
            if len(self.data) == 5:
                try:
                    package = BitStuffing.packaging(
                        data=self.data, port=self.write_port.port
                    )
                    package = BitStuffing.bit_stuffing(package)
                    PortManager.send_package(self.write_port, package)
                    self.bytes_sended += len(
                        BitStuffing.bit_stuffing(
                            BitStuffing.packaging(self.data, self.write_port.port)
                        ).encode()
                    )
                    self.log(f"Sent: {package}")
                    self.last_package = package
                    self.update_status()
                    self.data = ""
                except Exception as e:
                    QMessageBox.warning(self, "Error", "Failed: Port is not listening.")
                    self.clear_input()  # Очистка поля ввода при ошибке

    def write_text(self, byte: str):
        self.output_text.insertPlainText(byte)
        cursor = self.output_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.output_text.setTextCursor(cursor)

    def clear_input(self):
        was_blocked = self.input_text.blockSignals(True)
        self.input_text.clear()
        self.input_text.previous_text = ""
        self.input_text.blockSignals(was_blocked)
        self.log("Cleared sending section")

    def clear_output(self):
        self.output_text.clear()
        self.log("Cleared receiving section")

    def log(self, message: str):
        message = message.replace("\n", "\\n")
        self.debug_text.appendPlainText(message)

    def highlight_stuffed_bits(self, package: str):
        str = ""
        is_found = False
        highlighted_package = package[:8]
        for bit in package[8:]:
            str += bit
            if str == constants.FLAG[:-1]:
                highlighted_package += str
                highlighted_package += "["
                is_found = True
                str = ""
            elif len(str) == 7:
                highlighted_package += str[0]
                str = str[1:]
            else:
                if is_found:
                    highlighted_package += bit
                    highlighted_package += "]"
                    is_found = False
                    str = ""

        if str != "":
            highlighted_package += str

        highlighted_package = highlighted_package.replace("\n", "\\n")

        return highlighted_package

    def update_status(self):
        # Обновление статуса
        sending_port_info = "Sending port: not selected"
        receiving_port_info = "Receiving port: not selected"

        if self.write_port.is_open:
            sending_port_info = (
                f"Sending port: {self.write_port.name.split('/')[-1]} "
                f"(Baudrate = {self.write_port.baudrate}, "
                f"bytesize = {self.write_port.bytesize}, "
                f"parity = {self.write_port.parity}, "
                f"stopbits = {self.write_port.stopbits})"
            )

        if self.read_port.is_open:
            receiving_port_info = (
                f"Receiving port: {self.read_port.name.split('/')[-1]} "
                f"(Baudrate = {self.read_port.baudrate}, "
                f"bytesize = {self.read_port.bytesize}, "
                f"parity = {self.read_port.parity}, "
                f"stopbits = {self.read_port.stopbits})"
            )
        highlighted_output = self.highlight_stuffed_bits(self.last_package)
        self.status_text.clear()
        self.status_text.appendPlainText(sending_port_info)
        self.status_text.appendPlainText(receiving_port_info)
        self.status_text.appendPlainText(f"Bytes transmitted = {self.bytes_sended}\n")
        self.status_text.appendPlainText(f"Last package: {highlighted_output}\n")

    def closeEvent(self, event):
        """Закрытие программы и закрытие портов."""
        if self.read_port.is_open:
            self.read_port.close()
        if self.write_port.is_open:
            self.write_port.close()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
