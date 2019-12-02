import _thread
import queue
import socket, select
import os
import time
from threading import Lock
from config import *

class TCP:
    def __init__(self, outerQueue, ackQueue):
        self.buffer = queue.Queue(maxsize = WINDOW_SIZE)
        self.sendQueue = queue.Queue(maxsize = WINDOW_SIZE)
        self.packet_id = 0
        self.outerQueue = outerQueue
        self.ackQueue = ackQueue
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
                print("sending data to", ip, pck_id)
                sock.sendto(data, (ip, TCP_PORT))
                _thread.start_new_thread(self.persist, ((ip, pck_id, data, is_ack), ) )

    def send(self, ip, data):
        while not self.ack[self.packet_id]:
            self.packet_id = (self.packet_id+1)%PACKET_ID_CYCLE
        found = self.packet_id
        self.ack[found] = False
        data = str.encode(str(self.packet_id).zfill(3)+",")+data
        data = data+(b'0' * (PACKET_SIZE-len(data)) )
        self.sendQueue.put((ip, found, data, False))
        return found
            
    def buffer_handler(self):
        while True:
            data = self.buffer.get(block=True)
            dataHeader = data[:100].decode('ascii').split(",")
            pck_id = int(dataHeader[0])
            if dataHeader[1] == "ACK":
                self.ack[pck_id] = True
                self.ackQueue.put((pck_id, int(dataHeader[2])))
                continue
            if dataHeader[1] != "WindowProbe":
                self.outerQueue.put( data[4:] )
            rwnd = WINDOW_SIZE-self.buffer.qsize()-2
            self.sendQueue.put((dataHeader[2], pck_id, str.encode(str(pck_id)+",ACK,"+str(rwnd)), True))
            time.sleep(1)

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

class FlowControl:
    def __init__(self, tcp, ackQueue, host_ip):
        self.tcp = tcp
        self.lock = Lock()
        self.rwnd = 1
        self.host_ip = host_ip
        self.onAir = 0
        self.ackQueue = ackQueue
        self.target_ip = None
        self.ack = [True for i in range(PACKET_ID_CYCLE)]
        _thread.start_new_thread(self.rwnd_reader, ())
        _thread.start_new_thread(self.window_prober, ())

    def window_prober(self):
        probe_message = "WindowProbe,"+self.host_ip
        while True:
            if self.onAir != 0 and self.onAir < self.rwnd:
                self.tcp.send( self.target_ip, probe_message )
            time.sleep(0.1)

    def rwnd_reader(self):
        while True:
            pck_id, rwnd = self.ackQueue.get(block=True)
            self.lock.acquire()
            self.rwnd = max( rwnd , 1 )
            if not self.ack[pck_id]:
                self.ack[pck_id] = True
                self.onAir -= 1
            self.lock.release()

    def send(self, ip, data):
        while True:
            if self.onAir < self.rwnd:
                break
        self.target_ip = ip
        self.lock.acquire()
        pck_id = self.tcp.send(ip, data)
        self.ack[pck_id] = False
        self.onAir += 1
        self.lock.release()



