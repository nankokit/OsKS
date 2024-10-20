import random
from math import ceil, log2

import constants


def get_fcs_size():
    return ceil(log2(constants.DATA_SIZE + 1))


def fcs_from_package(package: str):
    return package[-get_fcs_size() :]


def hamming_code(data: str):
    fcs = ""
    fcs_size = get_fcs_size()
    for i in range(0, fcs_size):
        sum = 0
        for j in range(2**i, len(data) + 1, (2**i) * 2):
            bits = data[j - 1 : j + (2**i) - 1]
            for bit in bits:
                if bit != "\n":
                    sum ^= int(bit)
        fcs += str(sum)
    return fcs


def check_and_correct(data: str, code: str):
    code_now = hamming_code(data)
    if code == code_now:
        return data
    pos = 0
    for i in range(0, get_fcs_size()):
        if code[i] != code_now[i]:
            pos += 2**i
    data_list = list(data)
    data_list[pos - 1] = "0" if data_list[pos - 1] == "1" else "1"
    return "".join(data_list)


def distort_data(data: str):
    data_list = list(data)
    p = random.randint(1, 10)
    if p <= 3:
        pos = random.randint(0, len(data) - 1)
        if data_list[pos] != "\n":
            data_list[pos] = "0" if data_list[pos] == "1" else "1"
    return "".join(data_list)
