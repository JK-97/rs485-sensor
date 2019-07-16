# -*- coding: utf-8 -*-
import edgebox
import argparse
import socket, fcntl, struct 
from usbutils.deviceutils import UsbDevice
from time import sleep ,time
parser = argparse.ArgumentParser(description = 'this is a description')
parser.add_argument("-s","--serial",type = str,help="serial",default="/dev/ttyUSB0")
parser.add_argument("-b","--baudrate",type = int,help="baudrate",default = 9600)
parser.add_argument("-t","--timestep",type = int,help="timestep",default = 0.2)
parser.add_argument("-a","--hostaddress",type = str,help="hostaddress",default ='192.168.0.158')
parser.add_argument("-p","--statsdport",type = int,help="statsdport",default =8125)
parser.add_argument("-f","--filepath",type = str,help="filepath",default ="/app/my-vol/setting.json")
args = parser.parse_args()



class Rs485Driver:

    def __init__(self, serial_port=args.serial, baud_rate=args.baudrate, time_step=args.timestep, host=args.hostaddress, statsd_port=args.statsdport,filepath =args.filepath):
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.time_step = time_step
        self.host = host
        self.statsd_port = statsd_port
        self.filepath =filepath
      	


    def run(self):
        edgebox.setup(local_host="172.17.0.1")
        serialobj = UsbDevice(serial_port=self.serial_port, baud_rate=self.baud_rate,filepath=self.filepath)
        n = 1
        starttime = time()
        while True:
            stepstarttime = time()
            alldata = serialobj.read_all_data()
            sleep(0.12)
            stepfinshtime = time()
            print("steptime =" + str(stepfinshtime-stepstarttime))
            print("--------------------------------{}---------------------------------".format(n))
            n +=1
            for per_device_data in alldata:
                #所有设备存储data第一位是设备id信息。数据结构请查看read_all_data()
                device_id = per_device_data["id"]
                device_data = per_device_data["data"]
                
                for k,v in device_data.items():
                    if type(v) != str:
                        send_metric = "{}".format(k)
                        send_tags = {"id":"{}".format(device_id)}
                        sender = edgebox.monitor.create_gauge(send_metric,tags=send_tags)
                        sender.record(v)
                        print({send_metric+str(send_tags):v})

