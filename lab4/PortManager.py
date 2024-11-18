import os
import random
import time

import serial

import constants
import HammingCode


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


# def send_byte(port: serial.Serial, byte: str):
#     port.write(byte.encode())


# def get_byte(port: serial.Serial):
#     str = b""
#     try:
#         while True:
#             str += port.read()
#             try:
#                 str.decode()
#                 break
#             except:
#                 pass
#         return str.decode()
#     except:
#         pass


def send_package(port: serial.Serial, package: str):
    port.write(package.encode())


def get_package(port: serial.Serial):
    try:
        return port.read_all().decode()
    except:
        return None


def send_byte(port: serial.Serial, bit: str):
    collis_info = ""
    attempt_count = 0
    while True:
        while free_channel():
            pass
        port.write(bit.encode())
        if collision():
            port.write("j".encode())
            collis_info += "!"
            attempt_count += 1
            if attempt_count > 10:
                break
            else:
                # sleep_time = get_backoff(attempt_count)
                # print(sleep_time)
                # time.sleep(sleep_time)
                time.sleep(get_backoff(attempt_count))
        else:
            collis_info += "."
            break
    return collis_info


def get_byte(port: serial.Serial):
    try:
        return port.read().decode()
    except:
        return None


def full_packet(packet: str):
    return (
        len(packet)
        == len(constants.FLAG) + 4 + 4 + constants.DATA_SIZE + HammingCode.fcs_size()
    )


def free_channel():
    p = random.randint(1, 10)
    if p <= 3:
        return True
    return False


def collision():
    p = random.randint(1, 10)
    if p <= 3:
        return True
    return False


def get_backoff(attempt_number: int):
    r = random.randint(0, 2**attempt_number)
    return constants.SLOT_TIME * r
