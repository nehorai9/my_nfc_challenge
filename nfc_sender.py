import socket
import crc
import nfc_consts

IP = '142.93.107.1'
PORT = '8082'
CRC16_A_ARGS = (16, "CRC16_A", 0x1021, 0xC6C6, 0x0000, True, True, True)
RECV_LEN = 1024


class NFC(object):
    CRC_LEN = 4
    PAGE_BYTES_LEN = 4
    NAK_CODES = {'00': 'NAK for invalid argument (i.e. invalid page address)', '01': 'NAK for parity or CRC error',
                 '04': 'NAK for invalid authentication counter overflow', '05': 'NAK for EEPROM write error',
                 '06': 'NAK for unsupported command'}
    ACK_CODE = '0A'
    CNT_ADDRESS = '02'
    SIG_ADDRESS = '00'
    AUTH0_ADDRESS = 3
    AUTH0_LEN = 1
    NFC213_END_PAGE = '27'
    NFC215_END_PAGE = '81'
    NFC216_END_PAGE = 'E1'
    VERSION_CODE = '60'
    CFG_CODE = '66'
    READ_CODE = '30'
    FAST_READ_CODE = '3A'
    PWD_AUTH_CODE = '1B'
    WRITE_CODE = 'A2'
    READ_CNT_CODE = '39'
    READ_SIG_CODE = '3C'

    def __init__(self, ip, port, crc_args, check_crc=True, return_crc=False, recv_len=RECV_LEN, translate_naks=False):
        self.ip = ip
        self.port = port
        self.check_crc = check_crc
        self.return_crc = return_crc
        self.recv_len = recv_len
        self.crc = crc.CrcModel(*crc_args)
        self.translate_naks = translate_naks

    def _generic_msgs(self, msgs):
        """
        send generic messages to the NFC device
        :param msgs: a list of messages
        :return: a list of responses and dict with mapping of message and response
        """
        recvs = []
        recvs_map = {}
        s = socket.create_connection((self.ip, self.port))
        for msg in msgs:
            s.send(''.join([chr(int(msg[i:i + 2], 16)) for i, j in enumerate(msg) if i % 2 == 0]))
            r = s.recv(self.recv_len).encode('hex')
            recvs.append(r)
            if msg not in recvs_map:
                recvs_map[msg] = []
            recvs_map[msg].append(r)
        if self.check_crc:
            for recv in [r for r in recvs if r not in self.NAK_CODES.keys()]:
                if self._calc_crc(recv[:len(recv) - self.CRC_LEN]) != recv[-self.CRC_LEN:]:
                    print 'bad crc, {}'.format(recv)
        if not self.return_crc:
            recvs = [recv[:len(recv) - self.CRC_LEN] if len(recv) > self.CRC_LEN else recv for recv in recvs]
            recvs_map = {k: [recv[:len(recv) - self.CRC_LEN] if len(recv) > self.CRC_LEN else recv for recv in v] for
                         (k, v) in recvs_map.items()}
        if self.translate_naks:
            recvs = [
                recv if recv not in self.NAK_CODES.keys() else self.NAK_CODES[recv] for
                recv in recvs]
            recvs_map = {k: [
                recv if recv not in self.NAK_CODES.keys() else self.NAK_CODES[recv] for
                recv in v] for (k, v) in recvs_map.items()}
        return recvs, recvs_map

    def _calc_crc(self, msg):
        """
        computes and return the crc result of the message
        :param msg: string that represent hex bytes
        :return: crc result of the message
        """
        return self.crc.compute(msg)

    def _add_crc_to_msgs(self, msgs):
        """
        adds the crc result for every message and return the messages ready to send
        :param msgs: list of strings that every message represent in hex bytes
        :return: list of messages with crc
        """
        return [msg + self._calc_crc(msg) for msg in msgs]

    def get_version(self):
        """
        get the version of the NFC device
        :return: a list of responses and dict with mapping of message and response
        """
        msgs = [self.VERSION_CODE]
        msgs = self._add_crc_to_msgs(msgs)
        return self._generic_msgs(msgs)

    def read_data(self, start_page='00', password=None):
        """
        read 16 bytes (4 pages) of data from the NFC device
        :param start_page: start page address to read
        :param password: password for authentication and read protected data
        :return: a list of responses and dict with mapping of message and response
        """
        msgs = []
        if password:
            msgs.append(self.PWD_AUTH_CODE + password)
        msgs.append(self.READ_CODE + start_page)
        msgs = self._add_crc_to_msgs(msgs)
        return self._generic_msgs(msgs)

    def fast_read(self, start_page='00', end_page='23', password=None):
        """
        read data between start page address and end page address (include)
        :param start_page: start page address to read
        :param end_page: end page address to read (include)
        :param password: password for authentication and read protected data
        :return: a list of responses and dict with mapping of message and response
        """
        msgs = []
        if password:
            msgs.append(self.PWD_AUTH_CODE + password)
        msgs.append(self.FAST_READ_CODE + start_page + end_page)
        msgs = self._add_crc_to_msgs(msgs)
        recv = self._generic_msgs(msgs)
        if password:
            recv_data = ''.join(recv[0][1:])
        else:
            recv_data = ''.join(recv[0])
        if recv_data not in (self.NAK_CODES.keys() + self.NAK_CODES.values()):
            print recv_data.decode('hex')
        else:
            print 'bad response', recv_data, self.NAK_CODES[recv_data]
        return recv

    @staticmethod
    def _print_cfg_struct(cfg0, cfg1, detailed=False):
        """
        print NFC struct configuration
        :param cfg0: cfg0 data for the device
        :param cfg1: cfg1 data for the device
        :param detailed: the level of detail of the print
        """
        mirror, cfg0_reserved, mirror_page, auth0 = cfg0.decode('hex')[0].encode('hex'), cfg0.decode('hex')[1].encode(
            'hex'), cfg0.decode('hex')[2].encode('hex'), cfg0.decode('hex')[3].encode('hex')
        access, cfg1_reserved = cfg1.decode('hex')[0].encode('hex'), cfg1.decode('hex')[1:].encode('hex')
        if detailed:
            mirror_bin = bin(int(mirror, 16))[2:].zfill(8)[::-1]
            access_bin = bin(int(access, 16))[2:].zfill(8)[::-1]
            print nfc_consts.CFG_STRUCT_DETAILED_STR.format(mirror=mirror, mirror_bin=mirror_bin[::-1],
                                                            mirror_reserved=mirror_bin[0:2] + mirror_bin[3],
                                                            strg_mod_en=mirror_bin[2], mirror_byte=mirror_bin[4:6],
                                                            mirror_conf=mirror_bin[6:8],
                                                            cfg0_reserved=cfg0_reserved, mirror_page=mirror_page,
                                                            auth0=auth0, access=access, access_bin=access_bin[::-1],
                                                            access_reserved=access_bin[5], authlim=access_bin[0:3],
                                                            nfc_cnt_pwd_prot=access_bin[3],
                                                            nfc_cnt_en=access_bin[4], cfglck=access_bin[6],
                                                            prot=access_bin[7], cfg1_reserved=cfg1_reserved)
        else:
            print nfc_consts.CFG_STRUCT_NOT_DETAILED_STR.format(mirror=mirror, cfg0_reserved=cfg0_reserved,
                                                                mirror_page=mirror_page, auth0=auth0, access=access,
                                                                cfg1_reserved=cfg1_reserved)

    def _get_cfg(self):
        """
        get configuration bytes of the NFC device
        :return: a list of responses and dict with mapping of message and response
        """
        msgs = [self.CFG_CODE]
        msgs = self._add_crc_to_msgs(msgs)
        return self._generic_msgs(msgs)

    def get_cfg(self, detailed=False):
        """
        get and pretty print configuration bytes of the NFC device
        :param detailed: the level of detail of the print
        :return: a list of responses and dict with mapping of message and response
        """
        recv = self._get_cfg()
        recv_data = recv[0][0]
        if recv_data not in (self.NAK_CODES.keys() + self.NAK_CODES.values()):
            cfg0, cfg1 = recv_data[:4*2], recv_data[4*2:]
            print 'cfg0: {}, cfg1: {}'.format(cfg0, cfg1)
            self._print_cfg_struct(cfg0, cfg1, detailed)
        else:
            print 'bad response', recv_data, self.NAK_CODES[recv_data]
        return recv

    def write_data(self, data, address):
        """
        write one page to the NFC device
        :param data: one page (4 bytes) of data to write
        :param address: page address
        :return: a list of responses and dict with mapping of message and response
        """
        msgs = [self.WRITE_CODE+address+data]
        msgs = self._add_crc_to_msgs(msgs)
        return self._generic_msgs(msgs)

    def compatibility_write(self):
        raise NotImplementedError

    def read_cnt(self, address=CNT_ADDRESS, password=None):
        """
        read the NFC device counter configuration
        if None maybe NFC_CNT_EN is disabled
        (the counter feature is off) (bit no. 4 in ACCESS cfg)
        or NFC_CNT_PWD_PROT is enabled
        (the counter can be protected by password and requires authentication) (bit no. 3 in ACCESS cfg)
        :param address: NFC counter address
        :param password: password for authentication and read protected data
        :return: a list of responses and dict with mapping of message and response
        """
        msgs = []
        if password:
            msgs.append(self.PWD_AUTH_CODE + password)
        msgs.append(self.READ_CNT_CODE+address)
        msgs = self._add_crc_to_msgs(msgs)
        return self._generic_msgs(msgs)

    def read_sig(self, address=SIG_ADDRESS):
        """
        The READ_SIG command returns an IC specific, 32-byte ECC signature, to verify NXP
        Semiconductors as the silicon vendor. The signature is programmed at chip production
        and cannot be changed afterwards.
        :param address: RFU, is set to 00h
        :return: a list of responses and dict with mapping of message and response
        """
        msgs = [self.READ_SIG_CODE+address]
        msgs = self._add_crc_to_msgs(msgs)
        return self._generic_msgs(msgs)

    def _get_protected_address(self):
        """
        get protected address (AUTH0) from the cfg0 bytes
        :return: protected start page address
        """
        return self._get_cfg()[0][0][self.AUTH0_ADDRESS*2:(self.AUTH0_ADDRESS+self.AUTH0_LEN)*2]

    def read_protected(self, password, end_page=NFC213_END_PAGE):
        """
        read only protected by password data
        :param password: password for authentication and read protected data
        :param end_page: end page address to read (include)
        :return:
        """
        protected_address = self._get_protected_address()
        print 'read {} bytes of protected data!'.format(
            (1 + int(end_page, 16) - int(protected_address, 16)) * self.PAGE_BYTES_LEN)
        return self.fast_read(protected_address, end_page, password=password)


my_nfc = NFC(ip=IP, port=PORT, crc_args=CRC16_A_ARGS, return_crc=False, translate_naks=False)
# print my_nfc.get_version()
# print my_nfc.get_cfg()
# print my_nfc.get_cfg(detailed=True)
# print my_nfc.read_data()
# # print my_nfc.write_data('00112233', '00')
# print my_nfc.read_data('02', password='2468beaf')
# print my_nfc.fast_read()
# print my_nfc.fast_read('00', '00')
# print my_nfc.fast_read('00', 'ff', password='2468beaf')
# print my_nfc.read_cnt()
# print my_nfc.read_cnt(password='2468beaf')
# print my_nfc.read_sig()
protected_res, protected_res_map = my_nfc.read_protected(password='2468beaf')
print protected_res[1]
