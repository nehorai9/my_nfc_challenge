class CrcModel(object):
    CASRMASK16 = 0xFFFF
    BYTE_BITS_LEN = 8
    BYTE_HEX_LEN = 2

    def __init__(self, width, name, polynomial, initial, final_xor, input_reflected, result_reflected, little_endian):
        self.width = width
        self.name = name
        self.polynomial = polynomial
        self.initial = initial
        self.final_xor = final_xor
        self.input_reflected = input_reflected
        self.result_reflected = result_reflected
        self.cast_mask = self.CASRMASK16
        self.msb_mask = 0x01 << (self.width - 1)
        self.crc_table = self.calc_crc_table()
        self.little_endian = little_endian

    @staticmethod
    def reflect8(val):
        res_byte = 0
        for i in range(8):
            if (val & (1 << i)) != 0:
                res_byte |= ((1 << (7 - i)) & 0xFF)
        return res_byte

    def reflect_generic(self, val, width):
        res_byte = 0
        for i in range(self.width):
            if (val & (1 << i)) != 0:
                res_byte |= (1 << ((width-1) - i))
        return res_byte

    def calc_crc_table(self):
        crc_table = []
        for dividend in range(256):
            curr_byte = (dividend << (self.width - 8)) & self.cast_mask
            for bit in range(8):
                if (curr_byte & self.msb_mask) != 0:
                    curr_byte <<= 1
                    curr_byte ^= self.polynomial
                else:
                    curr_byte <<= 1
            crc_table.append(curr_byte & self.cast_mask)
        return crc_table

    def compute(self, data):
        crc = self.initial
        data_bytes = [int(data[i:i + 2], 16) for i, j in enumerate(data) if i % 2 == 0]
        for i in range(len(data_bytes)):
            cur_byte = data_bytes[i] & 0xFF
            if self.input_reflected:
                cur_byte = self.reflect8(cur_byte)
                # update the MSB of crc value with next input byte
                crc = (crc ^ (cur_byte << (self.width - 8))) & self.cast_mask
                # this MSB byte value is the index into the lookup table
                pos = (crc >> (self.width - 8)) & 0xFF
                # shift out this index
                crc = (crc << 8) & self.cast_mask
                # XOR-in remainder from lookup table using the calculated index
                crc = (crc ^ self.crc_table[pos]) & self.cast_mask
        if self.result_reflected:
            crc = self.reflect_generic(crc, self.width)
        crc = hex((crc ^ self.final_xor) & self.cast_mask)[2:]
        crc = crc.zfill(self.width/self.BYTE_BITS_LEN*self.BYTE_HEX_LEN)
        if self.little_endian:
            return ''.join([crc[i:i+2] for i, j in enumerate(crc) if i % 2 == 0][::-1])
        else:
            return crc
