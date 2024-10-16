def to_package(data: str, port: str):
    flag = "10000101"
    dest_addr = "0000"
    FCS = "0"
    src_addr = bin(int(port[-1:]))[2:]
    while len(src_addr) < 4:
        src_addr = "0" + src_addr
    return flag + dest_addr + src_addr + data + FCS


def from_package(package: str):
    return package[16:-1]


def bit_stuffing(packet: str):
    flag = "10000101"  # Флаг для исключения
    str = ""
    stuffed_packet = packet[:8]
    for bit in packet[8:]:
        str += bit
        # Проверка на флаг
        if str == flag:
            str += "0"  # Добавляем дополнительный бит
            stuffed_packet += str
            str = ""
        elif str == "100000":
            str += "0"
            stuffed_packet += str
            str = ""
        if len(str) == 6:
            stuffed_packet += str[0]
            str = str[1:]
    if str != "":
        stuffed_packet += str
    return stuffed_packet


def de_bit_stuffing(packet: str):
    str = ""
    destuffed_packet = packet[:8]
    for bit in packet[8:]:
        str += bit
        if str[:-1] == "100000":
            destuffed_packet += str[:-1]
            str = ""
        if len(str) == 7:
            destuffed_packet += str[0]
            str = str[1:]
    if str != "":
        destuffed_packet += str
    return destuffed_packet


def get_stuffed_bits(packet: str):
    str = ""
    stuffed_bits = "0" * 8
    for bit in packet[8:]:
        str += bit
        if str[:-1] == "100000":
            stuffed_bits += "0" * 6 + "1"
            str = ""
        if len(str) == 7:
            stuffed_bits += "0"
            str = str[1:]
    if str != "":
        stuffed_bits += "0" * len(str)
    return stuffed_bits
