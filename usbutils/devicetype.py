# -*- coding: utf-8 -*-
"""
* @package:devicetype
* @author: shenmingjie
* @version: V1.0
* @data: 2019.04.25
"""
from usbutils.crc16utils import add_crc16_code
from abc import abstractmethod

class BaseDevice:
    """
    * @className: BaseDevice
    * @packageName: devicetype
    * @description: 设备基类
    """
    FIXED_READ_COMMAND = ""
    FIXED_WRITE_COMMAND = ""
    # 指令固定字段
    LENGTH_READ_RESPONE = 0
    LENGTH_WRITE_RESPONE = 0
    # 数据的长度，用于检验
    def get_read_command(self, id):
        """
        * @methodsName: get_read_command
        * @description: 获取对应设备类型的读指令
        * @param:  id：设备id
        * @return: String
        * @throws: 
        """

        command_before_crc = id + self.FIXED_READ_COMMAND
        command_after_crc = add_crc16_code(command_before_crc)
        return command_after_crc

    def get_write_command(self, id, toid):
        """
        * @methodsName: get_write_command
        * @description: 获取对应设备类型的写指令
        * @param:  id：设备id
        * @return: String
        * @throws: 
        """
        command_before_crc = id + self.FIXED_WRITE_COMMAND + toid
        command_after_crc = add_crc16_code(command_before_crc)
        return command_after_crc

    @abstractmethod
    def translate_data(self, sources_data):
        """
        * @methodsName: translate_data
        * @description: 将原始16进制数据翻译成可读数据
        * @param:  sources_data：设备返回的16进制数据
        * @return: String
        * @throws: 
        """
        return None

class WsdDevice(BaseDevice):
    # 温度湿度传感器
    FIXED_READ_COMMAND = " 03 00 02 00 02"
    FIXED_WRITE_COMMAND = " 10 00 00 00 01 02 00 "
    LENGTH_READ_RESPONE = 9
    LENGTH_WRITE_RESPONE = 8
  

    def translate_data(self, sources_data):
        responeId = sources_data[:2]
        temperature = sources_data[6:10]
        humidity = sources_data[10:14]

        if temperature:
            temperatureRes = int(temperature, base=16)/10
        if humidity:
            humidityRes = int(humidity, base=16)/10
        return {"id":responeId,"data":{"temperature":temperatureRes,"humidity":humidityRes}}


class YwDevice(BaseDevice):
    # 烟雾报警传感器
    FIXED_READ_COMMAND = " 03 00 00 00 01"
    FIXED_WRITE_COMMAND = " 06 0b 00 00"
    LENGTH_READ_RESPONE = 7
    LENGTH_WRITE_RESPONE = 6
 
    def translate_data(self, sources_data):
        responeId = sources_data[:2]
        Smoke_concentration = sources_data[6:10]

        if Smoke_concentration:
            Smoke_concentration = int(Smoke_concentration, base=16)
        return {"id":responeId,"data":{"Smoke_concentration":Smoke_concentration}}

class GzDevice(BaseDevice):
    # 光照传感器
    FIXED_READ_COMMAND = " 03 00 02 00 01"
    FIXED_WRITE_COMMAND = " 10 00 00 00 01 02 00 "
    LENGTH_READ_RESPONE = 7
    LENGTH_WRITE_RESPONE = 8
 
    def translate_data(self, sources_data):
        responeId = sources_data[:2]
        brightness = sources_data[6:10]

        if brightness:
            brightness = int(brightness, base=16)

        return {"id":responeId,"data":{"brightness":brightness}}


class HwDevice(BaseDevice):
    # 人体红外传感器
    FIXED_READ_COMMAND = " 03 00 04 00 01"
    FIXED_WRITE_COMMAND = " 10 00 00 00 01 02 00 "
    LENGTH_READ_RESPONE = 7
    LENGTH_WRITE_RESPONE = 8
 
    def translate_data(self, sources_data):
        responeId = sources_data[:2]
        if_entry = sources_data[6:10]
        if_entry = int(if_entry, base=16)/10
        if if_entry:
            if_entry = 1
        else:
            if_entry = 0
        return {"id":responeId,"data":{"if_entry":if_entry}}

