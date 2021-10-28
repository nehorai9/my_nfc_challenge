CFG_STRUCT_NOT_DETAILED_STR = 'mirror: {mirror}, cfg0_reserved:{cfg0_reserved}, mirror_page: {mirror_page}, auth0: {auth0}, access: {access}, cfg1_reserved:{cfg1_reserved}'

CFG_STRUCT_DETAILED_STR = """*) mirror: {mirror}h<=>{mirror_bin}b\r\nbits no. 0, 1, 3 [{mirror_reserved}b] are reserved\r\nbit no. 2 [{strg_mod_en}b] is for STRG_MOD_EN: STRG MOD_EN defines the modulation mode
0b ... strong modulation mode disabled
1b ... strong modulation mode enabled\r\nbits no. 4, 5 [{mirror_byte}b] are for MIRROR_BYTE: The 2 bits define the byte position within the page defined by the MIRROR_PAGE
byte (beginning of ASCII mirror)\r\nbits no. 6,7 [{mirror_conf}b] are for MIRROR_CONF: Defines which ASCII mirror shall be used, if the ASCII mirror is enabled by a valid
the MIRROR_PAGE byte
00b ... no ASCII mirror
01b ... UID ASCII mirror
10b ... NFC counter ASCII mirror
11b ... UID and NFC counter ASCII mirror\r\n*) cfg0_reserved:{cfg0_reserved}. Reserved for future use - implemented. Write all bits and bytes denoted as RFUI as
0b.\r\n*) mirror_page: {mirror_page}. MIRROR_Page defines the page for the beginning of the ASCII mirroring
A value >03h enables the ASCII mirror feature\r\n*) auth0: {auth0}. AUTH0 defines the page address from which the password verification is required.
Valid address range for byte AUTH0 is from 00h to FFh.
If AUTH0 is set to a page address which is higher than the last page from the user
configuration, the password protection is effectively disabled.\r\n*) access: {access}h<=>{access_bin}b\r\nbit no. 5 [{access_reserved}b] is reserved\r\nbits no. 0-2 [{authlim}b] are for AUTHLIM: Limitation of negative password verification attempts
000b ... limiting of negative password verification attempts disabled
001b-111b ... maximum number of negative password verification attempts\r\nbit no. [{nfc_cnt_pwd_prot}b] 3 is for NFC_CNT_PWD_PROT: NFC counter password protection
0b ... NFC counter not protected
1b ... NFC counter password protection enabled
If the NFC counter password protection is enabled, the NFC tag will only respond
to a READ_CNT command with the NFC counter value after a valid password
verification\r\nbit no. 4 [{nfc_cnt_en}b] is for NFC_CNT_EN: NFC counter configuration
0b ... NFC counter disabled
1b ... NFC counter enabled
If the NFC counter is enabled, the NFC counter will be automatically increased at
the first READ or FAST_READ command after a power on reset\r\nbit no. 6 [{cfglck}b] is for CFGLCK: Write locking bit for the user configuration
0b ... user configuration open to write access
1b ... user configuration permanently locked against write access, except PWD and
PACK\r\nbit no. 7 [{prot}b] is for PROT: One bit inside the ACCESS byte defining the memory protection
0b ... write access is protected by the password verification
1b ... read and write access is protected by the password verification\r\n*) cfg1_reserved:{cfg1_reserved}. Reserved for future use - implemented. Write all bits and bytes denoted as RFUI as
0b."""