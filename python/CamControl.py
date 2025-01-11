# -*- coding: utf-8 -*-
"""
Created on Sat Jul  6 10:32:22 2024

@author: hht70
"""

import time
import threading
import struct
import socket

from datetime import datetime
from enum import Enum

#CRC校验
def crc16(data):
    crc = 0x0000  # 初始值为0x0000
    polynomial = 0x1021  # CRC16多项式

    for byte in data:
        crc ^= (byte << 8) & 0xFFFF
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ polynomial
            else:
                crc <<= 1
            crc &= 0xFFFF

    return crc

#从UDP接受byte流并解析的状态机的状态量
class parseState_e(Enum):
	PHASE_HEAD1 = 1
	PHASE_HEAD2 = 2
	PHASE_CTRL = 3
	PHASE_LEN1 = 4
	PHASE_LEN2 = 5
	PHASE_SEQ1 = 6
	PHASE_SEQ2 = 7
	PHASE_ID = 8
	PHASE_DATA = 9
	PHASE_CRC1 = 10
	PHASE_CRC2 = 11



#CamSender类，有两个线程，分别负责：
#thread1(task1),负责向云台发送消息，包括云台速度（CMD_ID:0x07）与请求云台姿态数据（CMD_ID:0x0D）
#thread2(task2),负责接受云台回传的数据并解析
class CamSender:
    def __init__(self,ip, port):
        #定义了两个线程与其回调函数（task1与task2）
        self.thread1 = threading.Thread(target=self.task1)
        self.thread2 = threading.Thread(target=self.task2)
        
        #摄像机端口的IP与端口
        self.ip = ip
        self.port = port
        self.s_temp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        #print(ip)
        #print(str(port))
        #self.s_temp.bind((ip,port))
        
        #相机角速度（yaw与pitch）
        self.cur_turn_yaw = 0
        self.cur_turn_pitch = 0
        
        #状态机的状态变量
        self.parseState = parseState_e.PHASE_HEAD1
        
        #接收缓冲区
        self.receiveBuf = [0]*256
        #数据长度
        self.dataLen = 0
        #接收数据计数值
        self.recivedDataCnt = 0
        self.CRC = [0]*2
        self.phaseDone = 0
        #云台三轴角度与角速度
        self.land_roll_deg = 0
        self.land_pitch_deg = 0
        self.land_yaw_deg = 0
        self.land_roll_deg_s = 0
        self.land_pitch_deg_s = 0
        self.land_yaw_deg_s = 0
    #开启两个线程 
    def start_threads(self):
        
        self.thread1.start()
        self.thread2.start()
    
    #设置云台角速度的接口函数
    def set_cur_turn(self, yaw, pitch):
        self.cur_turn_yaw = int(yaw)
        self.cur_turn_pitch = int(pitch)
    
    def get_attitude(self):
        return [self.land_yaw_deg, self.land_pitch_deg, self.land_roll_deg,
                self.land_yaw_deg_s, self.land_pitch_deg_s, self.land_roll_deg_s]
    #用状态机解析UDP回传的比特流
    def parseGimbalG1Data(self, receive_byte):
        ret = False
        #PHASE_HEAD1与PHASE_HEAD2阶段：默认是0x55与0x66
        if self.parseState ==  parseState_e.PHASE_HEAD1:
            if 0x55 == receive_byte:
                self.receiveBuf[0] = receive_byte
                self.parseState = parseState_e.PHASE_HEAD2
            else:
                self.parseState = parseState_e.PHASE_HEAD1
        elif self.parseState == parseState_e.PHASE_HEAD2:
            if 0x66 == receive_byte:
                self.receiveBuf[1] = receive_byte
                self.parseState = parseState_e.PHASE_CTRL
            else:
                self.parseState = parseState_e.PHASE_HEAD1
            #PHASE_CTRL阶段：不重要
        elif self.parseState == parseState_e.PHASE_CTRL:
            self.receiveBuf[2] = receive_byte;
            self.parseState = parseState_e.PHASE_LEN1
            #PHASE_LEN1与PHASE_LEN2阶段：当前帧数据域字节长度
        elif self.parseState == parseState_e.PHASE_LEN1:
            self.receiveBuf[3] = receive_byte
            self.parseState = parseState_e.PHASE_LEN2
        
        elif self.parseState == parseState_e.PHASE_LEN2:
            self.receiveBuf[4] = receive_byte
            self.parseState = parseState_e.PHASE_SEQ1
            #PHASE_SEQ1与PHASE_SEQ2：帧的序列，不重要
        elif self.parseState == parseState_e.PHASE_SEQ1:
            self.receiveBuf[5] = receive_byte
            self.parseState = parseState_e.PHASE_SEQ2
            
        elif self.parseState == parseState_e.PHASE_SEQ2:
            self.receiveBuf[6] = receive_byte
            self.parseState = parseState_e.PHASE_ID
        
            #PHASE_ID：当前命令的ID
        elif self.parseState == parseState_e.PHASE_ID:
            self.receiveBuf[7] = receive_byte
            #将数据接收计数器清零，准备收数据
            self.recivedDataCnt = 0
            #将数据长度清零            
            self.dataLen = 0
            #解析当前数据长度
            self.dataLen = int.from_bytes((self.receiveBuf[3].to_bytes(1, 'little') + 
                            self.receiveBuf[4].to_bytes(1, 'little') ), 'little')
            #如果数据长度大于0，进入PHASE_DATA阶段
            if self.dataLen > 0:
                self.parseState = parseState_e.PHASE_DATA
            #否则，跳过PHASE_DATA，直接进入PHASE_CRC1
            else:
                self.parseState = parseState_e.PHASE_CRC1
        #PHASE_DATA阶段：接受dataLen个字节的数据，将其放入self.receiveBuf中，从self.receiveBuf[8]开始存放
        elif self.parseState == parseState_e.PHASE_DATA:
            self.receiveBuf[8+self.recivedDataCnt] = receive_byte
            
            self.recivedDataCnt = self.recivedDataCnt + 1
            
            if self.recivedDataCnt >= self.dataLen:
                self.parseState = parseState_e.PHASE_CRC1
        #PHASE_CRC1与PHASE_CRC2：CRC校验阶段
        elif self.parseState == parseState_e.PHASE_CRC1:
            self.CRC[0] = receive_byte
            self.parseState = parseState_e.PHASE_CRC2
        elif self.parseState == parseState_e.PHASE_CRC2:
            
            self.CRC[1] = receive_byte
            
            # print("dataLen:"+str(self.dataLen))
            receiveBufUnsigned = self.receiveBuf[0:8+self.recivedDataCnt]
            
            
            tmpBytes = b''
            for receiveBufUnsignedInt in receiveBufUnsigned:
                tmpBytes = tmpBytes + receiveBufUnsignedInt.to_bytes(1, 'little')
            
            
            
            tmpCRC = crc16(tmpBytes)
            realCRC = int.from_bytes((self.CRC[0].to_bytes(1, 'little')) + 
                                    (self.CRC[1].to_bytes(1, 'little')), 'little')
            # print(self.receiveBuf[0:8+self.recivedDataCnt])
            # print("tmpBytes"+ tmpBytes.hex())
            # print("tmpCRC: "+ str(hex(tmpCRC)))
            # print("realCRC: "+ str(hex(realCRC)))
            #如果CRC校验通过，则返回True
            if tmpCRC == realCRC:
                ret = True
                
            #回到PHASE_HEAD1，开启下一轮
            self.parseState = parseState_e.PHASE_HEAD1
        return ret

    
    def task1(self):
        while 1:
            #print("cur_turn_pitch" + str(self.cur_turn_pitch))
            #发送角速度给云台，定义云台速度帧（CMD_ID:0x07，见siyi a8 mini手册）
            buffDataSend = 0x0000000000
            buffDataSend = buffDataSend | 0x55
            buffDataSend = buffDataSend | ((0x66)<< 8*1)
            buffDataSend = buffDataSend | ((0x01)<< 8*2)
            buffDataSend = buffDataSend | ((0x02)<< 8*3)
            buffDataSend = buffDataSend | ((0x00)<< 8*4)
            buffDataSend = buffDataSend | ((0x00)<< 8*5)
            buffDataSend = buffDataSend | ((0x00)<< 8*6)
            buffDataSend = buffDataSend | ((0x07)<< 8*7)
            #将int类型的角速度转化为bytes类型，小端模式，带符号
            buffdata_cur_yaw_byte = self.cur_turn_yaw.to_bytes(1, 'little',signed=True)
            buffdata_cur_pitch_byte = self.cur_turn_pitch.to_bytes(1, 'little',signed=True)
            
            #将两个角速度的byte进行拼接，低字节在前
            buffdata_cur_byte = buffdata_cur_yaw_byte + buffdata_cur_pitch_byte
            
            #将剩下的部分也转化为bytes流，小端模式，无符号，与buffdata_cur_byte进行凭拼接
            buffdata_byte = buffDataSend.to_bytes(8, 'little',signed=True) + buffdata_cur_byte
            #CRC校验，将CRC校验和附在最后两个字节上
            tmp_crc = crc16(buffdata_byte)
            tmp_crc_bytes = tmp_crc.to_bytes(2, 'little')
            tmp_buffdata_byte_all = buffdata_byte + tmp_crc_bytes
            #发送
            self.s_temp.sendto(tmp_buffdata_byte_all, (self.ip, self.port))
            #print("send "+str(tmp_buffdata_byte_all.hex()))
            #print(receive_data.hex())
            #print("send")
            #print("Current date and time:", datetime.now())
            #定义云台姿态请求帧
            buffDataSend = 0x0000000000
            buffDataSend = buffDataSend | 0x55
            buffDataSend = buffDataSend | ((0x66)<< 8*1)
            buffDataSend = buffDataSend | ((0x01)<< 8*2)
            buffDataSend = buffDataSend | ((0x00)<< 8*3)
            buffDataSend = buffDataSend | ((0x00)<< 8*4)
            buffDataSend = buffDataSend | ((0x00)<< 8*5)
            buffDataSend = buffDataSend | ((0x00)<< 8*6)
            buffDataSend = buffDataSend | ((0x0d)<< 8*7)
            buffDataSend = buffDataSend | ((0xe8)<< 8*8)
            buffDataSend = buffDataSend | ((0x05)<< 8*9)
            buffdataSend_byte = buffDataSend.to_bytes(10, 'little')
            
            self.s_temp.sendto(buffdataSend_byte, (self.ip, self.port))
            #print("send")
            
            
            time.sleep(0.01)
            
            continue
    #接受线程
    def task2(self):
        while 1:
            #接受数据
            receive_data, client_address = self.s_temp.recvfrom(1024)
            # print("=======================================")
            # print(receive_data.hex())
            #进行解析并分类处理
            for byte in receive_data:
                if self.parseGimbalG1Data(byte):
                    if self.receiveBuf[7] == 0x07:
                        # print("get ack")
                        continue
                    elif self.receiveBuf[7] == 0x0d:
                        # print("get angle")
                
                        self.land_yaw_deg = int.from_bytes((self.receiveBuf[8].to_bytes(1, 'little') + 
                                                             self.receiveBuf[9].to_bytes(1, 'little')),
                                                            byteorder='little',signed=True)
                        # print("self.land_yaw_deg", str(self.land_yaw_deg))
                        
                        self.land_pitch_deg = int.from_bytes((self.receiveBuf[10].to_bytes(1, 'little') + 
                                                             self.receiveBuf[11].to_bytes(1, 'little')),
                                                            byteorder='little',signed=True)
                        # print("self.land_pitch_deg", str(self.land_pitch_deg))
                        self.land_roll_deg = int.from_bytes((self.receiveBuf[12].to_bytes(1, 'little') + 
                                                             self.receiveBuf[13].to_bytes(1, 'little')),
                                                            byteorder='little',signed=True)
                        # print("self.land_roll_deg", str(self.land_roll_deg))
                        
                        self.land_yaw_deg_s = int.from_bytes((self.receiveBuf[14].to_bytes(1, 'little') + 
                                                             self.receiveBuf[15].to_bytes(1, 'little')),
                                                            byteorder='little',signed=True)
                        # print("self.land_yaw_deg_s", str(self.land_yaw_deg_s))
                        
                        self.land_pitch_deg_s = int.from_bytes((self.receiveBuf[16].to_bytes(1, 'little') + 
                                                             self.receiveBuf[17].to_bytes(1, 'little')),
                                                            byteorder='little',signed=True)
                        # print("self.land_picth_deg_s", str(self.land_pitch_deg_s))
                        
                        self.land_roll_deg_s = int.from_bytes((self.receiveBuf[18].to_bytes(1, 'little') + 
                                                             self.receiveBuf[19].to_bytes(1, 'little')),
                                                            byteorder='little',signed=True)
                        # print("self.land_roll_deg_s", str(self.land_roll_deg_s))

                
            continue
        

if __name__== "__main__":
    ip = '192.168.144.25'
    port = 37260
    camSender = CamSender(ip, port)
    camSender.start_threads()
    
    while 1:

        # camSender.set_cur_turn(20, 20)
        # time.sleep(1)
        # camSender.set_cur_turn(0, 0)
        # time.sleep(1)
        # camSender.set_cur_turn(-20, -20)
        print(camSender.get_attitude())
        time.sleep(0.1)
        continue