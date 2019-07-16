#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
* @package:deviceutils
* @author: shenmingjie
* @version: V1.0
* @data: 2019.04.25
"""
import serial
import binhex
import json
import logging

from time import sleep, time
from usbutils.devicetype import *
from usbutils.crc16utils import add_crc16_code, byte16_to_str
from usbutils.myexception import NonDeviceException, NonDataException, InvalidDataException


logger = logging.getLogger("device info")
logger.setLevel(logging.DEBUG)
# 建立一个filehandler来把日志记录在文件里，级别为debug以上
fh = logging.FileHandler("spam.log",encoding="utf-8")
fh.setLevel(logging.DEBUG)
# 建立一个streamhandler来把日志打在CMD窗口上，级别为error以上
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# 设置日志格式
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
fh.setFormatter(formatter)
#将相应的handler添加在logger对象中
logger.addHandler(ch)
logger.addHandler(fh)


WAIT_RECV = 0.12     # 接受等待时长


class UsbDevice:


    def __init__(self, serial_port='/dev/ttyUSB0', baud_rate=9600, time_step="10", filepath=""):
        self.time_step = time_step
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.serial_op = serial.Serial(
            serial_port, baud_rate, timeout=0.02)        # 连接端口号
        self.filepath = filepath
        if self.serial_op.isOpen():
            logging.info("open serial success")
        else:
            logging.warning("open serial failed")

    def read_one_data(self, device_id):  # 获取单个设备数据数据
        device_dict = self.find_device()
        device_type = device_dict[device_id]
        clean_data = self.__fetch_one(
            device_id=device_id, device_type=device_type)
        return clean_data

    def read_all_data(self):  # 获取全部设备数据
        """
        * @methodsName: read_all_data
        * @description: 获取settinig中注册设备的数据
        * @param:  
        * @return: list[dict,dict,....]
        * @throws: 
        """
        buffer = []
        device_dict = self.find_device()
        for device_id, device_type in device_dict.items():            # 轮询注册设备，并连接设备获取数据
            clean_data = self.__fetch_one(
                device_id=device_id, device_type=device_type)
            sleep(WAIT_RECV)
            buffer.append(clean_data)
        return buffer

        """
        * @buffer structure

        [
            {
            id:"01",
            data:{"humidity":value,
                "temperature":value}
            },
            {
            id:"02",
            data:{"brightness":value}
            }
        ]
        """


    def __fetch_one(self, device_id, device_type):      # 连接单个设备获取数据
        """
        * @methodsName: __fetch_one
        * @description: 获取数据，和校验数据
        * @param:  id:设备id  toid：写入的id  device_type:设备类型
        * @return: dict
        * @throws: NonDataException，InvalidDataException
        """

        try:
            device_obj = self.__make(device_type)         # 创建设备对象
        except:
            logger.error("无此设备类型{}".format(device_type))
        command_after_crc = device_obj.get_read_command(device_id)
        command_after_crc_16_byte = bytearray.fromhex(
            command_after_crc)       # 转换成字节流
        self.serial_op.write(command_after_crc_16_byte)
        sleep(WAIT_RECV) # 主要性能参数，快了会丢失数据
        non_check_data = self.__recv(self.serial_op)  
                   # 获取数据
        try:
            check_data = UsbDevice.sources_check(
                non_check_data, device_obj.LENGTH_READ_RESPONE)             # 检查数据
            clean_data = device_obj.translate_data(check_data)
        except NonDataException as e:
            logger.error(
                e.message + "id = {0} devecetype = {1}".format(device_id, device_type))
            clean_data = {"id": device_id, "data": {
                "device_type": "{}".format(device_type), "message": "该设备异常"}}
        except InvalidDataException as e:
            logger.error(e.message)
            clean_data = {"id": device_id, "data": {
                "device_type": "{}".format(device_type), "message": "该设备异常"}}

        return clean_data

    def find_device(self):  # 获取设备数据表
        with open(self.filepath, "r", encoding='utf-8') as f:
            setting = json.load(f)
            find_res = setting['device_list']
        return find_res

    def __make(self, device_type):    # 返回一个设别类型实例
        if device_type == 0:
            return WsdDevice()
        elif device_type == 1:
            return YwDevice()
        elif device_type == 2:
            return GzDevice()
        elif device_type == 3:
            return HwDevice()
        else:
            raise NonDeviceException()

    def __recv(self, serial):   # 检查接口是否有参数，有则返回

        while True:
            data = serial.read_all()
            if data != '':
                break
        return data

    def load_id(self, toid, device_type, id="01"):   # 注册设备id
        """
        * @methodsName: LoadId
        * @description: 注册设备id
        * @param:  id:设备id  toid：写入的id  device_type:设备类型
        * @return: 
        * @throws: NonDataException，InvalidDataException
        """
        def register(id, toid, device_type):    # 将设备注册在settings文件中
            load_dict = {}
            with open(self.filepath, "r", encoding='utf-8') as f:
                setting = json.load(f)
                device_dict = setting['device_list']
                device_dict.update({"{}".format(toid): device_type})
                if id != "01":
                    try:
                        device_dict.pop(id)
                    except:
                        logging.warning("注册表无此id{}".format(id))
                else:
                    pass
                setting.update({'device_list': device_dict})

                load_dict = setting
                logging.info("加载入文件完成...")
            with open(self.filepath, "r", encoding='utf-8') as f:
                logging.info("执行修改注册表操作")
                json.dump(load_dict, f, indent=4)
                logging.info("修改注册表成功")

        init_device = self.__make(device_type=device_type)
        command_after_crc = init_device.get_write_command(
            id=id, toid=toid)                                           # 创建设备对象
        command_after_crc_16_byte = bytearray.fromhex(
            command_after_crc)     # 转换成字节流
        self.serial_op.write(command_after_crc_16_byte)
        # 设备距离长时，这里可以等待
        non_check_data = self.__recv(self.serial_op)    # 获取数据
        try:
            check_data = UsbDevice.sources_check(
                sources_data=non_check_data, respond_length=init_device.LENGTH_WRITE_RESPONE)
        except NonDataException as e:
            logger.error(
                e.message + "id = {0} devecetype = {1}".format(id, device_type))
        except InvalidDataException as e:
            logging.exception(e.message)

        if check_data:
            logging.info("修改id成功")
            register(id=id,
                     toid=toid, device_type=device_type)
        else:
            logging.warning("修改id失败")

    @classmethod
    def sources_check(cls, sources_data, respond_length):  # 原始数据检查校验
        """
        * @methodsName: sources_check
        * @description: 检查返回的数据参数，respond_length在devicetyple.py中创建对象获取
        * @param:  sources_data:原始数据  respond_length:正确返回数据长度
        * @return: string
        * @throws: NonDataException，InvalidDataException
        """

        if len(sources_data) == 0:
            raise NonDataException(code = sources_data)
        if len(sources_data) != respond_length:
            raise InvalidDataException(code  = sources_data)
        res = byte16_to_str(sources_data[:-2])
        cheack_data = add_crc16_code(res).upper().replace(" ", "")
        sources_data = byte16_to_str(sources_data).upper().replace(
            " ", "")        # 收到的数据有时小写又是大写保证可以顺利执行判断
        if cheack_data != sources_data:
            raise InvalidDataException(code = cheack_data +" no equal " + sources_data )
        else:
            logging.info("正确数据")
            return cheack_data


# if __name__ == '__main__':

    # UsbDevice(serial_port="COM3", baud_rate=9600).read_one_data(device_id="02")
    # 建立COM3 9600端口对象，获取单个设备的数据
    # starttime = time()
    # UsbDevice(serial_port="/dev/ttyUSB0", baud_rate=9600).read_all_data()
    # finshtime = time()
    # UsbDevice(serial_port="/dev/ttyUSB0", baud_rate=9600).load_id(
    #     id="01", toid="09", device_type=2)
    # 建立COM3 9600端口对象，修改id ，id缺省时默认修改01的设备
