import _thread
import queue
import socket, select
import os
import time
from config import *

class TCP:
    def __init__(self, outerQueue):
        self.buffer = queue.Queue(maxsize = WINDOW_SIZE)
        self.sendQueue = queue.Queue(maxsize = WINDOW_SIZE)
        self.packet_id = 0
        self.outerQueue = outerQueue
        self.ack = [True for i in range(PACKET_ID_CYCLE)]
        _thread.start_new_thread(self.receiver, () )
        _thread.start_new_thread(self.buffer_handler, () )
        _thread.start_new_thread(self.sender, ())

    def persist(self, data):
        time.sleep(1)
        self.sendQueue.put(data)

    def sender(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        while True:
            ip, pck_id, data, is_ack = self.sendQueue.get(block=True)
            if is_ack:
                sock.sendto(data, (ip, TCP_PORT))
            elif not self.ack[pck_id]:
                sock.sendto(data, (ip, TCP_PORT))
                _thread.start_new_thread(self.persist, ((ip, pck_id, data, is_ack), ) )

    def send(self, ip, data):
        while not self.ack[self.packet_id]:
            self.packet_id = (self.packet_id+1)%PACKET_ID_CYCLE
        self.ack[self.packet_id] = False
        data = str.encode(str(self.packet_id).zfill(3)+",")+data
        data = data+(b'0' * (PACKET_SIZE-len(data)) )
        self.sendQueue.put((ip, self.packet_id, data, False))
            
    def buffer_handler(self):
        while True:
            data = self.buffer.get(block=True)
            print(data.decode('ascii'))
            data = data.decode('ascii').split(",")
            pck_id = int(data[0])
            if data[1] == "ACK":
                self.ack[pck_id] = True
                continue
            self.outerQueue.put( ",".join(data[1:]))
            self.sendQueue.put((data[2], pck_id, str.encode(str(pck_id)+",ACK"), True))

    def receiver(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('', TCP_PORT))
        sock.setblocking(False)
        while True:
            result = select.select([sock],[],[])
            packet = result[0][0].recv(PACKET_SIZE)
            if self.buffer.full():
                continue
            self.buffer.put(packet)
