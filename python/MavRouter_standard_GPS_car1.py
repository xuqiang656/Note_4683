#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from pymavlink import mavutil
import time
import threading
import struct
import socket
import decimal
import rospy
import math
import configparser
import os
from geometry_msgs.msg import Twist, PoseStamped
from transforms3d.euler import quat2euler
class MocapRouter(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app
        self.mocapNum = app.droneNum
        self.daemon = True
        rospy.init_node('MocapRouter', anonymous=True)
        for i in range(self.mocapNum):
            drone = app.drones[i]
            rospy.Subscriber("/vrpn_client_node/droneyee" +
                             str(i+1)+"/pos_sync", PoseStamped, drone.rosPosCb)
            rospy.Subscriber("/vrpn_client_node/droneyee" +
                             str(i+1)+"/vel_sync", PoseStamped, drone.rosVelCb)

    def run(self):
        rospy.spin()
class MatlabReceiver(threading.Thread):
    def __init__(self, app, ip, port):
        threading.Thread.__init__(self)
        self.port = port
        self.ip = ip
        self.uavNum = app.droneNum
        self.drones = app.drones
        self.mUavs = []
        self.daemon = True
        for i in range(self.uavNum):
	        s_temp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	        s_temp.bind((self.ip, port+2*i))
	        self.mUavs.append(s_temp)

    def run(self):
        while True:
            for i in range(self.uavNum):
                data, addr = self.mUavs[i].recvfrom(1024)
                UAV_data = struct.unpack('<dddddddd', data[0:64])
                #print("recv matlab to uav %d====(%f,%f,%f)"%(UAV_data[0],UAV_data[1],UAV_data[2],UAV_data[3]))
                #print("UAV_data[0] === %d"%(UAV_data[0]))
                #print("i+1 === %d"%(i+1))
                if abs(UAV_data[0] - (i+1))==0:
                        self.drones[i].cmdVel[0] = UAV_data[1]
                        self.drones[i].cmdVel[1] = UAV_data[2]
                        self.drones[i].cmdVel[2] = UAV_data[3]
                        self.drones[i].cmdVel[3] = UAV_data[4]
                        self.drones[i].cmdVel[4] = UAV_data[5]
                        self.drones[i].cmdVel[5] = UAV_data[6]
                        self.drones[i].cmdVel[6] = UAV_data[7]
                        self.drones[i].cmd_vel_update = True
                        self.drones[i].matlabControlInited = True
                        #print("recv matlab to uav %d====(%f,%f,%f,%f)"%(UAV_data[0],UAV_data[1],UAV_data[2],UAV_data[3],UAV_data[7]))
                        if UAV_data[7]>1:
                              print("recv matlab cmd %f====(%f)"%(UAV_data[0],UAV_data[7]))
                else:
                       print("fal")
# 通过udp将需要的飞机数据发送给Matlab,目前只发送了电池信息
# matlab地址和发送端口号（起始端口号作为参数传入）
# 每个飞机的端口号依次+1
# MocapRouter创建时需要传入app和matlab的ip地址和端口号
# MocapRouter继承于Thread,可使用start方法启动
class MatlabSender(threading.Thread):  
    def __init__(self,app,ip,port):  
        threading.Thread.__init__(self)  
        self.uavNum = app.droneNum
        self.drones = app.drones
        self.uavs = []
        self.ip = ip
        self.port = port
        self.daemon = True
        for i in range(self.uavNum):
	        s_temp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	        self.uavs.append(s_temp)
    def run(self):  
        while True:
            for i in range(self.uavNum):
                #if(self.drones[i].active):
                    UAV_data = struct.pack("<ddddddddddddddddddddd", (i + 1), self.drones[i].batInfo[0] ,self.drones[i].batInfo[1]/1000.0,
                    self.drones[i].localPosNED[0] ,self.drones[i].localPosNED[1],self.drones[i].localPosNED[2],     	 #LocalPosition
									  self.drones[i].attitude[0],self.drones[i].attitude[1],self.drones[i].attitude[2],			#attitude angle	
									  self.drones[i].HomePosition[0],self.drones[i].HomePosition[1],self.drones[i].HomePosition[2],		#HomePosition
									  self.drones[i].HomePosition[3],self.drones[i].HomePosition[4],self.drones[i].HomePosition[5], 
									  self.drones[i].visionPose[0],self.drones[i].visionPose[1],self.drones[i].visionPose[2],		#HomePosition
									  0,self.drones[i].connected,self.drones[i].system_status)   #status of uav
                    #print("send to matlab battery mav %d===(%f)===%d===%f"%((i+1),self.drones[i].batInfo[1],self.drones[i]._active,self.drones[i].system_status))
                    num1 = self.ip
                    num2 = self.port+2*i+1
                    self.uavs[i].sendto(UAV_data, (num1, num2))
            time.sleep(0.01) 
class Drone():
    # 初始化环境局
    def __init__(self, addr,nId):
        self.addr = addr
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
        self.nId = nId
        self.mavtype = 0
        self.autopilot = 0
        self.base_mode = 0
        self.custom_mode = 0
        self.system_status = 0
        self.connected = False
        self.cmd_vel_update = False
        self.matlabControlInited = False
        rospy.Subscriber("/droneyee"+str(self.nId)+"/mavros/vision_pose/pose", PoseStamped, self.rosPosCb)
        print("====drone %d launched with connect %s ==="%(self.nId,addr))
    # 回调函数，用于ros消息回调#/vrpn_client_node/droneyee%i/pos_sync
    def rosPosCb(self,msg):
        #ENU frame to NED
        self.visionPose[0] = msg.pose.position.y
        self.visionPose[1] = msg.pose.position.x
        self.visionPose[2] = -msg.pose.position.z
        self.visionPose[3] = msg.pose.orientation.w
        self.visionPose[4] = msg.pose.orientation.x
        self.visionPose[5] = msg.pose.orientation.y
        self.visionPose[6] = msg.pose.orientation.z
        #print("recv pos_sync %d,%f,%f,%f"%(self.nId,self.visionPose[0],self.visionPose[1],self.visionPose[2]))
    # 回调函数，用于ros消息回调#/vrpn_client_node/droneyee%i/vel_sync
    def rosVelCb(self,msg):
        self.visionPose[7] = msg.pose.position.x
        self.visionPose[8] = msg.pose.position.y
        self.visionPose[9] = msg.pose.position.z
    # 打开连接
    def open(self):
        try:
            print("Opening connection to %s" % (self.addr,))
            self.conn = mavutil.mavlink_connection(self.addr)
            self._active = True
            self.last_packet_received = time.time()  # lie
            self.last_pos_updated = time.time()
        except Exception as e:
            print("Connection to (%s) failed: %s" % (self.addr, str(e)))
            self._active = False
    # 切换到offboard模式，需要先发送期望数据再切换
    def arm(self):
        if self.connected:
            self.conn.mav.command_long_send(self.conn.target_system,self.conn.target_component,
                mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,0,
               1,0,0,0,0,0,0)
            print("Mav %d: arm" % (self.conn.target_system))
    def gotoGuided(self):
        if self.connected:
            #self.conn.wait_heartbeat(timeout=2)
            self.conn.mav.set_position_target_local_ned_send(0,       # time_boot_ms (not used)
                                                    0, 0,    # target system, target component
                                                    mavutil.mavlink.MAV_FRAME_LOCAL_NED, # frame
                                                    0b0000111111000111, # type_mask (only speeds enabled)
                                                    0, 0, 0, # x, y, z positions (not used)
                                                    0, 0, 0, # x, y, z velocity in m/s
                                                    0, 0, 0, # x, y, z acceleration (not used)
                                                    0, 0)    # yaw,)OFFBOARD
            #mode_id = self.conn.mode_mapping()["STABILIZE"]
            self.conn.mav.command_long_send(self.conn.target_system,self.conn.target_component,
                mavutil.mavlink.MAV_CMD_NAV_GUIDED_ENABLE,0,
                1,0,0,0,0,0,0)
            print("Mav %d: go guided " % (self.conn.target_system))
    # att_pos_mocap_send函数的用法需要查一下
    def update(self):
        if self.cmd_vel_update:
            self.cmd_vel_update = False
            self.conn.mav.set_position_target_local_ned_send(0,       # time_boot_ms (not used)
                                                    0, 0,    # target system, target component
                                                    mavutil.mavlink.MAV_FRAME_LOCAL_NED, # frame
                                                    0b0000111111000111, # type_mask (only speeds enabled)
                                                    0, 0, 0, # x, y, z positions (not used)
                                                    self.cmdVel[0], self.cmdVel[1], self.cmdVel[2], # x, y, z velocity in m/s
                                                    0, 0, 0, # x, y, z acceleration (not used)
                                                    0, 0)    # yaw,)
            print("send cmd vel to uav %d==(%f,%f,%f)"%(self.nId,self.cmdVel[0],self.cmdVel[1],self.cmdVel[2]))

        else:
            if not self.matlabControlInited:
                self.conn.mav.set_position_target_local_ned_send(0,       # time_boot_ms (not used)
                                                        0, 0,    # target system, target component
                                                        mavutil.mavlink.MAV_FRAME_LOCAL_NED, # frame
                                                        0b0000111111000111, # type_mask (only speeds enabled)
                                                        0, 0, 0, # x, y, z positions (not used)
                                                        0, 0, 0, # x, y, z velocity in m/s
                                                        0, 0, 0, # x, y, z acceleration (not used)
                                                        0, 0)    # yaw,) 
                #print("send cmd vel to uav %d==(%f,%f,%f)"%(self.nId,self.cmdVel[0],self.cmdVel[1],self.cmdVel[2]))

                                           
        [roll,pitch,yaw] = quat2euler([self.visionPose[3],self.visionPose[4],self.visionPose[5],self.visionPose[6]])
        #print("send vision pose to uav %d==(%f,%f,%f,%f,%f,%f)"%(self.nId,self.visionPose[0],self.visionPose[1],self.visionPose[2],roll,pitch,yaw))
        #self.conn.mav.vision_position_estimate_send(0,self.visionPose[0],self.visionPose[1],self.visionPose[2],roll,pitch,-yaw+math.pi/2)
    def recv_message(self):
        if self._active:
            while True:
                m = None
                try:
                    m = self.conn.recv_msg()
                except Exception as e:
                    print("Exception receiving message on addr(%s): %s" % (str(self.addr), str(e)))
                    self.conn.close()
                    m = None
                    break
                if m is None:
                    break
                self.last_packet_received = time.time()
                if  m.get_type() == "LOCAL_POSITION_NED":
                    now = time.time()
                    tt = now-self.last_pos_updated
                    self.last_pos_updated = now
                    if(tt>0.05):
                        print("Mav %d: RTT too long time %8.3f ms" % (self.conn.target_system,tt*1000))
                    self.localPosNED[0] = m.x
                    self.localPosNED[1] = m.y
                    self.localPosNED[2] = m.z
                    self.localPosNED[3] = m.vx
                    self.localPosNED[4] = m.vy
                    self.localPosNED[5] = m.vz
                    print("Mav %d: local pos (%f,%f,%f)" % (self.conn.target_system,m.x,m.y,m.z))
                elif m.get_type() == 'HEARTBEAT':
                    self.mavtype = m.type
                    self.autopilot = m.autopilot
                    self.base_mode = m.base_mode
                    self.custom_mode = m.custom_mode
                    self.system_status = m.system_status
                    #print("MAV ID === %d,system_status === %f"%(self.nId,m.system_status))
                    self.connected = True
                    #print("Mav %d: type=%d,autopilot=%d,base_mode=%d,custom_mode=%d" % (self.conn.target_system,m.type,m.autopilot,m.base_mode,m.custom_mode))
                elif m.get_type() == 'BATTERY_STATUS':
                    self.batInfo[1] = m.voltages[0]
                    self.batInfo[0] = m.battery_remaining
                    #print("Mav %d: battery (%f,%f)" % (self.conn.target_system,m.voltages[0],m.battery_remaining))
                elif m.get_type() == 'HOME_POSITION':
                    self.HomePosition[0] = m.latitude          	#degE7
                    self.HomePosition[1] = m.longitude		#degE7
                    self.HomePosition[2] = m.altitude		#mm
                    self.HomePosition[3] = m.x
                    self.HomePosition[4] = m.y
                    self.HomePosition[5] = m.z
                elif m.get_type() == 'ATTITUDE':
                    self.attitude[0] = m.roll
                    self.attitude[1] = m.pitch
                    self.attitude[2] = m.yaw
                    self.attitude[3] = m.rollspeed
                    self.attitude[4] = m.pitchspeed
                    self.attitude[5] = m.yawspeed
                    #print("Mav %d: attitude (%f,%f,%f)" % (self.conn.target_system,m.roll,m.pitch,m.yaw))
                elif m.get_type() == 'STATUSTEXT':
                    print("mav %d ,info message %d (%s)"%(self.conn.target_system,m.severity,m.text))
    # 关闭连接        
    def close(self):
        self.conn.close()
        self._active = False
    # 返回激活状态
    def active(self):
        return self._active
# MAVLinkRouter类用于接收和发送飞机的数据，保持所有飞机的连接状态
# MAVLinkRouter类有三个线程：
# connection_maintenance_thread线程用于维护所有飞机的连接状态
# receving_thread线程用于循环接收飞机发送来的数据
# 自己的主线程用于向飞机发送消息（这些数据通过由matlab线程和mocap线程接收过来），通过drone的update函数实现

# Drone类维护了一个和飞机的连接
# Drone提供了发送和接受飞机数据的接口
# Drone的连接字符串通过参数传入
# 连接参数addr的格式需要查一下？
class MAVLinkRouter(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)  
        self.connection_maintenance_target_should_live = False
        self.receving_thread_should_live = False
        self.inactivity_timeout = 5
        self.reconnect_interval = 2
        self.drones = app.drones
        self.uavNum = app.droneNum
        self.daemon = True
    # 这里面打开所有飞机的连接
    def create_connections(self):
        for dr in self.drones:
            dr.open()
        self.connection_maintenance_target_should_live = True
        self.receving_thread_should_live = True
    # 这个函数是connection_maintenance_thread线程的主函数，更新所有飞机的连接状态，每周期运行一次
    def maintain_connections(self):
        now = time.time()
        for dr in self.drones:
            if not dr.active():
                continue
            if now - dr.last_packet_received > self.inactivity_timeout:
                print("Connection (%s) timed out" % (dr.addr,))
                dr.close()
        for dr in self.drones:
            if not dr.active():
                if now - dr.last_connection_attempt > self.reconnect_interval:
                    dr.last_connection_attempt = now
                    dr.open()
    # 创建connection_maintenance_thread线程
    def create_connection_maintenance_thread(self):
        '''create and start helper threads and the like'''
        # 10Hz周期运行，调用maintain_connections
        def connection_maintenance_target():
            while self.connection_maintenance_target_should_live:
                self.maintain_connections()
                time.sleep(0.1)
        connection_maintenance_thread = threading.Thread(target=connection_maintenance_target)
        connection_maintenance_thread.setDaemon(True)
        connection_maintenance_thread.start()
    
    # 这个函数是receving_thread线程的主函数，接收飞机的数据，每周期运行一次
    def receiving_messages(self):
        for dr in self.drones:
            dr.recv_message()
    # 创建receving_thread线程
    def create_receving_thread(self):
        '''create and start receiving threads and the like'''
        # 100Hz周期运行，调用receiving_messages
        def receving_message_target():
            while self.receving_thread_should_live:
                self.receiving_messages()
                time.sleep(0.01)
        receving_thread = threading.Thread(target=receving_message_target)
        receving_thread.setDaemon(True)
        receving_thread.start()
    # 主线程，用于向飞机发送数据
    def run(self):
        self.create_connections()
        self.create_receving_thread()
        self.create_connection_maintenance_thread()
        # 先把所有飞机切换至offboard状态
        time.sleep(1)
        #for dr in self.drones:
        #    dr.gotoGuided()
        #    dr.arm()
        # 循环执行，向飞机发送数据，20Hz运行
        while True:
            # send messages
            for dr in self.drones:
            #for i in range(self.uavNum):
                if (dr.cmdVel[6]-3)==0:
                    dr.gotoGuided()
                    print('offboard %f'%(dr.cmdVel[6]))
                    dr.cmdVel[6] = 0
                    
                if (dr.cmdVel[6]-2)==0:
                    dr.arm()
                    dr.cmdVel[6] = 0
                         
                dr.update()
                #print('updating')
            time.sleep(0.01)

class RouterApp():  
    def __init__(self,args):
        BASEDIR=os.path.dirname(os.path.abspath(__file__))
        cf = configparser.ConfigParser()
        cf.read(os.path.join(BASEDIR,'mav_car.conf'))
        secs = cf.sections()
        opts=cf.options("mav")
        kvs=cf.items("mav")
        self.droneNum = cf.getint("mav","mav_num")
        #self.mocapRouter = MocapRouter(self)
        #self.matlabReceiver = MatlabReceiver(self,"127.0.0.1",25000)
	#rospy.init_node('mavconfig')
        self.drones = []

        print("MAV NUM === %d"%self.droneNum)
        for i in range(self.droneNum):
                port=cf.get("mav","mav_port"+str(i+1))
                drone =  Drone("udpin:0.0.0.0:"+port,i+1)
                self.drones.append(drone)
        
        #drone =  Drone("udpin:0.0.0.0:15553",3)
        #self.drones.append(drone)
        #drone =  Drone("udpin:0.0.0.0:15554",4)
        #self.drones.append(drone)
        #drone =  Drone("udpin:0.0.0.0:15555",5)
        #self.drones.append(drone)
        #drone =  Drone("udpin:0.0.0.0:15556",6)
        #self.drones.append(drone)
        #drone =  Drone("udpin:0.0.0.0:15557",7)
        #self.drones.append(drone)
        #drone =  Drone("udpin:0.0.0.0:15558",8)
        #self.drones.append(drone)
        #drone =  Drone("udpin:0.0.0.0:15559",9)
        #self.drones.append(drone)
        #drone =  Drone("udpin:0.0.0.0:15560",10)
        #self.drones.append(drone)
        #这里应该读写配置文件
        #for i in range(self.droneNum):
        #    drone = Drone()
        #    self.drones.append(drone)
        self.mavlinkRouter = MAVLinkRouter(self)
        #self.matlabSender = MatlabSender(self,"192.168.122.109",26100)
       # self.matlabReceiver = MatlabReceiver(self,"192.168.122.105",25000)
        self.matlabSender = MatlabSender(self,"127.0.0.1",28000)
        self.matlabReceiver = MatlabReceiver(self,"127.0.0.1",28000)


    def start_run(self):
        #self.mocapRouter.start()
        self.matlabReceiver.start()
        self.matlabSender.start()
        self.mavlinkRouter.start()

if __name__== "__main__":
    from optparse import OptionParser
    parser = OptionParser("MavRouter.py [options]")
    (opts, args) = parser.parse_args()
    drones = []
    rospy.init_node('MavRouter', anonymous=True)
    print("======init ros node MavRouter done!====")
    router = RouterApp(args)
    router.start_run()
    
    rospy.spin()
    

    # if len(args) == 0:
    #    print("Insufficient arguments")
    #    sys.exit(1)
