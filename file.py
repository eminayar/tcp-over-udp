users = {}

import _thread
import sys
import socket, select
import os
import time

os.system('clear')
host_name = socket.gethostname()
host_ip = "192.168.1.104"

PORT = 12345

## [<PacketId>,<data>]
class TCP:
    def __init__(self):
        self.PACKET_SIZE = 5
        self.MAXID = 10000
        self.packetCounter = 0
        _thread.start_new_thread(self.receiver, () )

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
            print(sock.getsockopt(socket.SOL_SOCKET,socket.SO_RCVBUF))
            time.sleep( 4 )
            pass
            



tcp_over_udp = TCP()

target_ip = "192.168.1.105"
while True:
    path = input("EXIT or message:")
    if path == "exit":
        exit(0)
    else:
        tcp_over_udp.sender(target_ip, b'10101' )
