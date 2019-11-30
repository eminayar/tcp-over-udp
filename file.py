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
    
    def send_file(self, ip, path):
        headers = "[" + host_ip + "," + path.split("/")[-1] + ","
        with open( path, "rb" ) as f:
            packet_index = 0 
            while True:
                packet_index += 1
                header_with_index = headers+str(packet_index) + ","
                chunk_size = self.PACKET_SIZE-len(str.encode(header_with_index+"]"))
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                self.sender(ip, str.encode(header_with_index)+chunk+str.encode("]"))

    def sender(self, ip, data):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data, (ip, PORT))

    def receiver(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', PORT))
        sock.setblocking(False)
        while True:
            result = select.select([sock],[],[])
            msg = result[0][0].recv(self.PACKET_SIZE).decode('ascii')
            print(msg)

tcp_over_udp = TCP()

target_ip = "192.168.1.37"
while True:
    path = input("EXIT or message:")
    if path == "exit":
        exit(0)
    else:
        tcp_over_udp.send_file(target_ip, path)

## [my_ip,filename,packet_index,packet]
