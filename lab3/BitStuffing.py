import constants
import HammingCode


def packaging(data: str, port: str):
    FCS = HammingCode.hamming_code(data)
    source_address = bin(int(port[-1:]))[2:]
    while len(source_address) < 4:
        source_address = "0" + source_address
    return constants.FLAG + constants.DEST_ADDR + source_address + data + FCS


def depackaging(package: str):
    return package[16 : -HammingCode.get_fcs_size()]


def bit_stuffing(package: str):
    str = ""
    stuffed_package = package[:8]
    for bit in package[8:]:
        str += bit
        if str == constants.FLAG[:-1]:
            str += "0"
            stuffed_package += str
            str = ""
        if len(str) == 7:
            stuffed_package += str[0]
            str = str[1:]
    if str != "":
        stuffed_package += str
    return stuffed_package


def de_bit_stuffing(package: str):
    str = ""
    destuffed_package = package[:8]
    for bit in package[8:]:
        str += bit
        if str[:-1] == constants.FLAG[:-1]:
            destuffed_package += str[:-1]
            str = ""
        if len(str) == 8:
            destuffed_package += str[0]
            str = str[1:]
    if str != "":
        destuffed_package += str
    return destuffed_package
