users = {}

import _thread
import sys
import socket, select
import os
import time

os.system('clear')
host_name = socket.gethostname() 
host_ip = "192.168.1.38"

PORT = 12345

class TCP:
    def __init__(self):
        self.PACKET_SIZE = 1500
        _thread.start_new_thread(self.receiver, () )
        pass

    def sender(self, ip, data):
        #data = 1500 bytes(max)#
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data, (ip, PORT))

    def receiver(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', PORT))
        sock.setblocking(False)
        result = select.select([sock],[],[])
        msg = result[0][0].recv(self.PACKET_SIZE).decode('ascii')
        print(msg)

tcp_over_udp = TCP()

target_ip = "192.168.1.37"
message = input("message: ")
tcp_over_udp.sender(target_ip, message.encode() )
