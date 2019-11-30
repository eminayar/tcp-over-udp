users = {}

import _thread
import sys
import socket
import os
import time

os.system('clear')
host_name = socket.gethostname() 
host_ip = 

PORT = 12345

class TCP:
    def __init__(self):
        _thread.start_new_thread(self.sender, (ip, data) )
        _thread.start_new_thread(self.receiver, () )
        pass

    def sender(ip, data):
        #data = 1500 bytes(max)#
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data, (ip, PORT))
        pass

    def receiver():
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', PORT))
        s.setblocking(False)
        result = select.select([s],[],[])
        msg = result[0][0].recv(bufferSize).decode('ascii')
        print(msg)
        pass

tcp_over_udp = TCP()

target_ip = "85.105.76.101"
message = input("message: ")
