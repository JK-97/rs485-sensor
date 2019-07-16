# -*- coding: utf-8 -*-


class MyException(Exception):
    def __init__(self,message="",code= ""):
        self.message =message
        self.code = code

class NonDeviceException(MyException):
    def __init__(self,message = '没有此设备',code=""):
        self.message =message
        self.code = code
class InvalidDataException(MyException):
    def __init__(self,message = "获得数据不完整",code=""):
        self.message = message
        self.code = code

class NonDataException(MyException):
    def __init__(self,message = "空数据，请检查是否接入此设备",code=""):
        self.message = message
        self.code = code