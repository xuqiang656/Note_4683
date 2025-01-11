# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 20:18:43 2024

@author: hht70
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 17:41:43 2024

@author: hht70
"""
import time
import threading
import struct
import socket


class Commnicator(threading.Thread):
    def __init__(self,ip, port):
        threading.Thread.__init__(self) 
        self.ip = ip
        self.port = port
        self.s_temp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._sendUartBuf = [0]*12
        self._recvUartBuf = [0]*12
    def send_cur_angle(cur_turn_yaw, cur_turn_pitch):
        
        while 1:
            continue
    def run(self):
        
        print("1")
    
    

if __name__== "__main__":
    buff = [0]*10
    ip = "192.168.144.25"
    port = 37260
    s_temp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while 1:
        time.sleep(1)
        buff[0] = 0x55
        buff[1] = 0x66
        buff[2] = 0x01
        buff[3] = 0x00
        buff[4] = 0x00
        buff[5] = 0x00
        buff[6] = 0x00
        buff[7] = 0x0d
        buff[8] = 0xe8
        buff[9] = 0x05
        #s_temp.sendto(buff, (ip, port))
        buffdata = 0x0000000000
        buffdata = buffdata | buff[0]
        buffdata = buffdata | ((buff[1])<< 8*1)
        buffdata = buffdata | ((buff[2])<< 8*2)
        buffdata = buffdata | ((buff[3])<< 8*3)
        buffdata = buffdata | ((buff[4])<< 8*4)
        buffdata = buffdata | ((buff[5])<< 8*5)
        buffdata = buffdata | ((buff[6])<< 8*6)
        buffdata = buffdata | ((buff[7])<< 8*7)
        buffdata = buffdata | ((buff[8])<< 8*8)
        buffdata = buffdata | ((buff[9])<< 8*9)

        buffdata_byte = buffdata.to_bytes(10, 'little')
        
        s_temp.sendto(buffdata_byte, (ip, port))

        receive_data, client_address = s_temp.recvfrom(1024)
        
        land_yaw_deg = struct.unpack('<h', receive_data[8:10])[0]
        land_pitch_deg = struct.unpack('<h', receive_data[10:12])[0]
        land_roll_deg = struct.unpack('<h', receive_data[12:14])[0]
        
        land_yaw_deg_s = struct.unpack('<h', receive_data[14:16])[0]
        land_pitch_deg_s = struct.unpack('<h', receive_data[16:18])[0]
        land_roll_deg_s = struct.unpack('<h', receive_data[18:20])[0]
        
        print("land_yaw_deg: " + str(land_yaw_deg))
        print("land_pitch_deg: " + str(land_pitch_deg))
        print("land_roll_deg: " + str(land_roll_deg))
        print(" ")
        print("land_yaw_deg_s: " + str(land_yaw_deg_s))
        print("land_pitch_deg_s: " + str(land_pitch_deg_s))
        print("land_roll_deg_s: " + str(land_roll_deg_s))
        print("==================================================")
   # 55 66 02 0c 00 44 00 0d // 1a 00 f9 f8 00 00 fc ff ff ff fd ff // 19 88
        