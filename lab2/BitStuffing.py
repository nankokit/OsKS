def packaging(data: str, port: str):
    flag = "10000101"
    destination_address = "0000"
    source_address = bin(int(port[-1:]))[2:]
    FCS = "0"
    while len(source_address) < 4:
        source_address = "0" + source_address
    return flag + destination_address + source_address + data + FCS


def depackaging(package: str):
    return package[16:-1]


def bit_stuffing(package: str):
    str = ""
    stuffed_package = package[:8]
    for bit in package[8:]:
        str += bit
        if str == "1000010":
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
        if str[:-1] == "1000010":
            destuffed_package += str[:-1]
            str = ""
        if len(str) == 8:
            destuffed_package += str[0]
            str = str[1:]
    if str != "":
        destuffed_package += str
    return destuffed_package
