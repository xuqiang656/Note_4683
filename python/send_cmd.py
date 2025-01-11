# -*- coding: utf-8 -*-
"""
Created on Wed Jun 26 21:16:28 2024

@author: hht70
"""

from pymavlink import mavutil
import time
import threading
import struct
import socket

Flag = 0

class Sender(threading.Thread):
    def __init__(self,ip, port,x0,y0,z0):
        threading.Thread.__init__(self)
        self.nId = port - 27000 + 1
        self.semaphore = threading.Semaphore(5)
        self.ip = ip
        self.port = port
        self.UAV_data=[0]*8
        self.s_temp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.startpos=[0]*3
        self.startpos[0] = x0
        self.startpos[1] = y0
        self.startpos[2] = z0
        
        self.UAV_data = [self.nId,x0,y0,z0,0,0,0,2]
    def set_UAVdata_pos(self, posX,posY,posZ):
        self.UAV_data = [self.nId, posX+self.startpos[0], 
                                  posY+self.startpos[1], 
                                  posZ+self.startpos[2], 
                                  0, 0, 0, 3]
        # self.UAV_data = [self.nId, posX+x0, 
        #                            posY+y0, 
        #                            posZ+z0, 
        #                            0, 0, 0, 3]
        
        
    def set_UAVdata_cmd(self,cmd):
        #arm
        if cmd == 1:
            self.UAV_data = [self.nId, 0,0,0,0,0,0,2]
        #offboard
        elif cmd == 2:
            self.UAV_data = [self.nId, 0,0,0,0,0,0,3]
        elif cmd == 3:
            self.UAV_data = [self.nId, 1,1,-2,0,0,0,3]
    def run(self):
        while True:
            #self.semaphore.acquire()
            tmpdata = struct.pack('<dddddddd', self.UAV_data[0],self.UAV_data[1],self.UAV_data[2],
                                                self.UAV_data[3],self.UAV_data[4],self.UAV_data[5],
                                                self.UAV_data[6],self.UAV_data[7])
            num1 = self.ip
            num2 = self.port
            #print(num2)
            self.s_temp.sendto(tmpdata, (num1, num2))
            time.sleep(0.01)

class Receiver(threading.Thread):
    def __init__(self,ip, port):
        threading.Thread.__init__(self) 
        self.ip = ip
        self.port = port
        self.nId = 0
        self._active = False
        self.last_packet_received = 0
        self.last_pos_updated = 0
        self.last_connection_attempt = 0
        self.cmdVel=[0]*7
        self.visionPose=[0]*9
        self.localPosNED=[0]*6
        self.attitude=[0]*6
        self.HomePosition=[0]*6
        self.batInfo=[0]*2
        self.mode=0
        self.conn = None
        self.mavtype = 0
        self.autopilot = 0
        self.base_mode = 0
        self.custom_mode = 0
        self.system_status = 0
        self.connected = False
        self.cmd_vel_update = False
        self.matlabControlInited = False
        
        self.s_temp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s_temp.bind((self.ip, port+1))
        print(port+1)
        self.flag = 0
    def run(self):
        while True:
            data, addr = self.s_temp.recvfrom(1024)
            
            UAV_data = struct.unpack('<ddddddddddddddddddddd', data[0:168])
            
            self.nId = UAV_data[0]
            self.batInfo[0] = UAV_data[1]
            self.batInfo[1] = UAV_data[2]
            
            self.localPosNED[0] = UAV_data[3]
            self.localPosNED[1] = UAV_data[4]
            self.localPosNED[2] = UAV_data[5]
            
            self.attitude[0] = UAV_data[6]
            self.attitude[1] = UAV_data[7]
            self.attitude[2] = UAV_data[8]
            
            self.HomePosition[0] = UAV_data[9]
            self.HomePosition[1] = UAV_data[10]
            self.HomePosition[2] = UAV_data[11]
            self.HomePosition[3] = UAV_data[12]
            self.HomePosition[4] = UAV_data[13]
            self.HomePosition[5] = UAV_data[14]
            
            self.visionPose[0] = UAV_data[15]
            self.visionPose[1] = UAV_data[16]
            self.visionPose[2] = UAV_data[17]
            ###
            self.connected = UAV_data[19]
            self.system_status = UAV_data[20]
            self.flag = 1
            

if __name__== "__main__":
    print("start")
    R = Receiver("127.0.0.1", 27000)
    
    R.start()
    while R.flag != 1:
        continue
    print("start pos:"+ str(R.localPosNED[0]) + ", " +
                      str(R.localPosNED[1]) + ", " + 
                      str(R.localPosNED[2]))
    print("Get Data")
    
    S = Sender("127.0.0.1", 27000, R.localPosNED[0], 
                                   R.localPosNED[1], 
                                   R.localPosNED[2])
    S.start()
    while 1:
        numlist = input().split()
        S.set_UAVdata_pos(float(numlist[0]), float(numlist[1]), float(numlist[2]))
        # if num == 1:
        #     S.set_UAVdata_cmd(1)
        # elif num == 3:
        #     S.set_UAVdata_cmd(3)
        # elif num == 4:
        #     S.set_UAVdata_pos(1.234, 1.234, -2.5)
        # elif num == 5:
        #     S.set_UAVdata_pos(2.234, 2.234, -2.5)\
        
        #S.semaphore.release()
        print("Sended")
        continue