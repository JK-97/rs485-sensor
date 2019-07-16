# -*- coding: utf-8 -*-
from crcmod import *
from binascii import *
def add_crc16_code(command_before_crc):
    """
    * @methodsName: add_crc16_code
    * @description: 将传感器指令添加crc校验位
    * @param:  command_before_crc：未添加crc校验的命令
    * @return: String
    * @throws:
    """
    crc16 = crcmod.mkCrcFun(
        0x18005, rev=True, initCrc=0xFFFF, xorOut=0x0000)
    data = command_before_crc.replace(" ", "")
    readcrcout = hex(crc16(unhexlify(data))).upper()
    str_list = list(readcrcout)
    if len(str_list) == 5:
        str_list.insert(2, '0')
    crc_data = "".join(str_list)
    command_after_crc = command_before_crc.strip()+' ' + \
        crc_data[4:]+' '+crc_data[2:4]
    # print('CRC16校验:', crc_data[4:]+' '+crc_data[2:4])
    # print('增加Modbus CRC16校验：>>>', command_after_crc)
    command_after_crc = ' ' + command_after_crc
    return command_after_crc


def byte16_to_str(data): 
    """
    * @methodsName: byte16_to_str
    * @description: 将字节16进制转化为字符串
    * @param:  data:16进制数据
    * @return: String
    * @throws: 
    """
    res = ""
    for i in data:
        num = str(hex(i))
        if len(num) < 4:
            num = "0"+num[2] + " "
        else:
            num = num[2:4] + " "
        res = res + num
    return res