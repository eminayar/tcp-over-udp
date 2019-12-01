users = {}

import _thread
import sys
import queue
import socket, select
import os
from threading import Lock
import time
from config import *

os.system('clear')
host_name = socket.gethostname()
host_ip = "192.168.1.104"

## [<PacketId>,<data>]
class TCP:
    def __init__(self):
        self.buffer = queue.Queue(maxsize = WINDOW_SIZE)
        self.sendQueue = queue.Queue(maxsize = WINDOW_SIZE)
        self.packet_id = 0
        self.ack = [False for i in range(PACKET_ID_CYCLE)]
        _thread.start_new_thread(self.receiver, () )
        _thread.start_new_thread(self.buffer_handler, () )
        _thread.start_new_thread(self.sender, ())


    def persist(self, data):
        time.sleep(1)
        sendQueue.put(data)

    def sender(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while True:
            ip, pck_id , data = self.sendQueue.get(block=True)
            if not self.ack[pck_id]:
                print("sending data")
                sock.sendto(data, (ip, PORT))
                _thread.start_new_thread(self.persist, ((ip, pck_id, data), ) )
            
    def buffer_handler(self):
        while True:
            data = self.buffer.get(block=True)
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
        tcp_over_udp.sendQueue.put((target_ip, 0, b'Hello World!') )
