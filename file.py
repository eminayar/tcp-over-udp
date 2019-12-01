users = {}

import _thread
import sys
import queue
import socket, select
import os
import time
from config import *

os.system('clear')
host_name = socket.gethostname()
host_ip = "192.168.1.104"

## [<PacketId>,<data>]
class TCP:
    def __init__(self):
        self.buffer = queue.Queue(maxsize = WINDOW_SIZE)
        _thread.start_new_thread(self.receiver, () )
        _thread.start_new_thread(self.queue_handler, () )

    def sender(self, ip, data):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data, (ip, PORT))

    def queue_handler(self):
        time.sleep(10)
        print("queue handler started")
        while True:
            data = buffer.get(block=True)
            print( data.decode('ascii') )


    def receiver(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', PORT))
        sock.setblocking(False)
        while True:
            result = select.select([sock],[],[])
            packet = result[0][0].recv(PACKET_SIZE)
            if self.buffer.full():
                continue
            self.buffer.put(packet)
            
            



tcp_over_udp = TCP()

target_ip = "192.168.1.105"
while True:
    path = input("EXIT or message:")
    if path == "exit":
        exit(0)
    else:
        tcp_over_udp.sender(target_ip, b'Hello World!' )
