users = {}
from config import *
from tcp import TCP, FlowControl

def announcement_listener(host_name, host_ip, tsocket ):
    import select, socket
    import time
    import _thread
    global users

    bufferSize = 1024
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', UDP_PORT))
    s.setblocking(False)
    while True:
        result = select.select([s],[],[])
        msg = result[0][0].recv(bufferSize).decode('ascii')
        usr, ip, tp = msg.split(',')
        usr = usr.strip()[1:]
        tp = tp.strip()[:-1]
        ip = ip.strip()
        if tp.strip() == 'announce' and ip != host_ip:
            if (usr not in users) or (usr in users and time.time()-users[usr][1] > 5):
                users[usr] = (ip,time.time())
                response_message = '[' + host_name + ',' + host_ip + ',response]'
                response_message += '0' * (96-len(response_message))
                tsocket.send( ip, str.encode(response_message) )

def tcp_listener(host_ip, dataStream):
    import socket
    import time
    global users

    chunklist = []
    numArrived = 0

    while True:
        binary = dataStream.get(block=True)
        data = binary[:96].decode("ascii").split(',')
        if( len(data) < 3 ):
            print("Unsupported message type")
            continue
        usr = data[0].strip()[1:]
        tp = data[2].strip().split("]")[0].strip()
        ip = data[1].strip()
        if tp == 'response':
            if (usr not in users) or (usr in users and time.time()-users[usr][1] > 5):
                users[usr] = (ip,time.time())
        elif tp == 'message':
            print(usr + ": " + data[3].strip().split("]")[0].strip())
        elif tp == 'file':
            filename = data[3]
            outOf = int(data[4])
            pck_index = int(data[5])
            pck_length = int(data[6].split("]")[0])
            chunk = binary[96:96+pck_length]
            print(data)
            if numArrived == 0:
                chunklist = [b'0' for i in range(outOf)]
            if chunklist[pck_index] != chunk:
                numArrived +=1
                chunklist[pck_index] = chunk
            if numArrived == outOf:
                numArrived = 0
                with open(filename, "wb+") as destination:
                    for chunk in chunklist:
                        destination.write( chunk )


import _thread
import sys
import socket
import os
import math
import queue
import time

os.system('clear')
username = input("Enter your username: ")
host_ip = HOST_IP
listenerQueue = queue.Queue()
streamAck = queue.Queue()
tsocket = TCP( listenerQueue, streamAck )
flow = FlowControl( tsocket, streamAck , host_ip)

try:
    _thread.start_new_thread( announcement_listener, ( username, host_ip, tsocket, ) )
    _thread.start_new_thread( tcp_listener, (host_ip, listenerQueue,  ) )
except:
    print ("Error: unable to start thread")

announce_message = '[' + username + ',' + host_ip + ',announce]'
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
print("Broadcasting...")
for _ in range(3):
    sock.sendto(str.encode(announce_message),('<broadcast>',UDP_PORT))

while True:
    command = input("Enter command(exit, list, message, file): \n")
    if command == 'exit':
        break
    if command == 'list':
        print( list(users.keys()) )
    elif 'message' in command:
        cmd = command.split(" ")
        response_message = '[' + username + ',' + host_ip + ',message,' + cmd[2].strip() + ']'
        response_message += '0' * (96-len(response_message))
        tsocket.send( users[cmd[1].strip()][0] , str.encode(response_message) )
    elif 'file' in command:
        to = command.split(" ")[1].strip()
        filepath = command.split(" ")[2].strip()
        filename = filepath.split("/")[-1]
        outOf = math.floor(os.path.getsize(filepath)/1400)
        if outOf*1400 != os.path.getsize(filepath):
            outOf += 1
        header = "["+username+","+HOST_IP+",file,"+filename+","+str(outOf)+","
        with open(filepath, "rb") as f:
            chunkCounter = 0
            while True:
                chunk = f.read( 1400 )
                if not chunk:
                    break
                data_header = str.encode(header+str(chunkCounter)+","+str(len(chunk))+"]" )
                data_header += b'0' * (96-len(data_header))
                flow.send( users[to][0], data_header+chunk )
                chunkCounter += 1
                
# 125,[<username>,<ip>,"file","filename",99999,23512,1400]