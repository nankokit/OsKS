import os

import serial

import BitStuffing


def get_all_ports():
    path = "/dev/"
    files = os.listdir(path)
    ports = []
    for file in files:
        if "tnt" in file:
            try:
                port = serial.Serial(path + file, exclusive=True)
                ports.append("tnt" + file[3])
                port.close()
            except:
                pass
    ports.reverse()
    return ports


def connect_to_port(port: str):
    try:
        ports = serial.Serial("/dev/tnt" + port[3], exclusive=True)
        return ports
    except:
        return serial.Serial()


def send_byte(port: serial.Serial, byte: str):
    port.write(byte.encode())


def get_byte(port: serial.Serial):
    str = b""
    try:
        while True:
            str += port.read()
            try:
                str.decode()
                break
            except:
                pass
        return str.decode()
    except:
        pass


def send_package(port: serial.Serial, package: str):
    port.write(package.encode())


def get_package(port: serial.Serial):
    try:
        return port.read_all().decode()
    except:
        return None
