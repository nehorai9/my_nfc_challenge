import crc
from itertools import chain, product

HEX_STRIP = [hex(i)[2:] for i in range(0, 16)]
CRC_TARGET = '4930'
FORMATTED_PARTIAL_INPUT = '1b{}beaf'
BLANK_MIN_LEN = 4
BLANK_MAX_LEN = 4


def bruteforce(strip, min_length, max_length):
    """
    returns all options of the strip characters in required length
    :param strip: list of relevant characters
    :param min_length: the minimum length of string to be returned
    :param max_length: the maximum length of string to be returned
    :return: generator of all options
    """
    return (''.join(char) for char in chain.from_iterable(product(strip, repeat=x)
                                                          for x in range(min_length, max_length+1)))


cac16a = crc.CrcModel(16, "CRC16_A", 0x1021, 0xC6C6, 0x0000, True, True, True)
for option in bruteforce(HEX_STRIP, BLANK_MIN_LEN, BLANK_MAX_LEN):
    input_bytes = FORMATTED_PARTIAL_INPUT.format(option)
    crc_res = cac16a.compute(input_bytes)
    if crc_res == CRC_TARGET:
        print 'The correct option is: {}, partial input: {}.\r\nfull content: {} equal to the target crc: {}.'.format(
            option, FORMATTED_PARTIAL_INPUT, input_bytes, CRC_TARGET)
