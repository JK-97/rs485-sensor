# rs485-sensor

### usage
pip3 install -r requirements.txt



### setting

    {
        "device_list":{
            "02":0,
            "03":1,
            "04":2
            }
    }
    

### config 
    parser.add_argument("-s","--serial",type = str,help="serial",default="/dev/ttyUSB0")
    parser.add_argument("-b","--baudrate",type = int,help="baudrate",default = 9600)
    parser.add_argument("-t","--timestep",type = int,help="timestep",default = 0.2)
    parser.add_argument("-a","--hostaddress",type = str,help="hostaddress",default ='192.168.0.158')
    parser.add_argument("-p","--statsdport",type = int,help="statsdport",default =8125)
    parser.add_argument("-f","--filepath",type = str,help="filepath",default ="/app/my-vol/setting.json")