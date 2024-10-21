import random
from math import ceil, log2

import constants


def fcs_size():
    return ceil(log2(constants.DATA_SIZE + 1))


def get_fcs(package: str):
    return package[-fcs_size() :]


def generate_hamming_code(data: str):
    fcs = ""
    for i in range(0, fcs_size()):
        parity_sum = 0
        for j in range(2**i, len(data) + 1, (2**i) * 2):
            segment = data[j - 1 : j + (2**i) - 1]
            for bit in segment:
                if bit != "\n":
                    parity_sum ^= int(bit)
        fcs += str(parity_sum)
    return "".join(fcs)


def validate_and_correct_data(received_data: str, received_code: str):
    generated_code = generate_hamming_code(received_data)
    if received_code == generated_code:
        return received_data

    error_position = 0

    for i in range(0, fcs_size()):
        if received_code[i] != generated_code[i]:
            error_position += 2**i

    data_list = list(received_data)

    data_list[error_position - 1] = "1" if data_list[error_position - 1] == "0" else "0"
    return "".join(data_list)


def introduce_random_error(data: str):
    data_list = list(data)
    error_chance = random.randint(1, 10)

    if error_chance <= 3:
        error_position = random.randint(0, len(data) - 1)
        if data_list[error_position] != "\n":
            data_list[error_position] = "1" if data_list[error_position] == "0" else "0"
    return "".join(data_list)
