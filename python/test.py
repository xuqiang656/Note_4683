import struct
import socket
import time
if __name__== "__main__":
	port = 27000
	host = "127.0.0.1" 
	s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM) 
	while 1:
		#struct.unpack('<dddddddd', data[0:64])
		a=int(input("commander"))
		try:
			
			if a==1:
				data = struct.pack('<dddddddd',1,0,0,0.1,0,0,0,0)
				s.sendto(data,(host,port))
			elif a==2:
				data = struct.pack('<dddddddd',1,0,0,0,0,0,0,2)
				s.sendto(data,(host,port))
			elif a==3:
				data = struct.pack('<dddddddd',1,0,0,0,0,0,0,3)
				s.sendto(data,(host,port))
		except EOFError:
			print("over")
		time.sleep(1)

        
