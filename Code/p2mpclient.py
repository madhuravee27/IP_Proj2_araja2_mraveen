import sys
import os
import math
import csv
from struct import *
from socket import *
from threading import *
import time
#from datetime import *

no_servers = len(sys.argv) - 4
SERVER_LIST = []
for i in range(1, no_servers + 1):
    SERVER_LIST.append(sys.argv[i])

SERVER_PORT = int(sys.argv[no_servers + 1])
FILE_NAME = sys.argv[no_servers + 2]
MSS = int(sys.argv[no_servers + 3])


def getMSS(filename, counter, mss_value):
    f = open(filename, 'rb')
    f.seek(counter*mss_value, 1)
    mss_data = f.read(mss_value)
    f.close()
    if(len(mss_data) < mss_value):
        for i in range(0, mss_value - len(mss_data)):
            mss_data = mss_data + ' '.encode('utf-8')
    return mss_data.decode('utf-8')

def carry_around_add(a, b):
    c = a + b
    return (c & 0xffff) + (c >> 16)

def calculate_checksum(data):
    checksum_value = 0
    for i in range(0, len(data), 2):
        #i = ord(i[0])<<8 | ord(i[1])
        if(i == (len(data)-1)):
            return ~checksum_value & 0xFFFF
        i = ord(data[i]) + (ord(data[i+1]) << 8)
        checksum_value = carry_around_add(checksum_value,i)
    return ~checksum_value & 0xFFFF

def get_segment(seq_num):
    #str_format =
    segment_format = Struct('I H H {}'.format(str(MSS) + 's'))
    segment_identifier = 21845
    data = getMSS(FILE_NAME, seq_num, MSS)
    return segment_format.pack(seq_num, segment_identifier, calculate_checksum(data), data.encode('utf-8'))

def parse_ack_segment(ack_segment):
    ack_segment_format = Struct('I H H')
    ack_segment_identifier = 43690

    unpacked_ack = ack_segment_format.unpack(ack_segment)
    #validation for ack_segment_identifier not performed
    return unpacked_ack[0]

def send_to_server(clientSocket, serverDetails, seq_num, segment_list, time_list, position, lock):
    try:

        clientSocket.settimeout(0.1)
        lock.acquire()
        start_time = time.time()
        clientSocket.sendto(get_segment(seq_num), serverDetails)
        ack_segment, serverAddress = clientSocket.recvfrom(4096)
        end_time = time.time()
        lock.release()
        segment_list[position] = parse_ack_segment(ack_segment)
        time_list[position] += (end_time - start_time)

    except timeout:
        lock.release()
        segment_list[position] = seq_num
        end_time = time.time()
        time_list[position] += (end_time - start_time)
        #print('Timeout, sequence number = ' + str(segment_list[position]))
    except :
        print('Exception occured')

def start():

    clientSocket = socket(AF_INET, SOCK_DGRAM)
    seq_num = 0
    file_size = os.path.getsize(FILE_NAME)
    no_of_segments = math.ceil(file_size/MSS)
    time_list = [0] * no_servers

    for cur_seq_num in range(no_of_segments):

        segment_list = [None] * no_servers
        thread_list = [None] * no_servers
        lock = Lock()

        for j in range(no_servers):
            thread_list[j] = Thread(name=j ,target=send_to_server, args=(clientSocket, (SERVER_LIST[j],SERVER_PORT), cur_seq_num, segment_list, time_list, j, lock))
            thread_list[j].start()
            thread_list[j].join()

        while 1:

            if cur_seq_num in segment_list:

                position = segment_list.index(cur_seq_num)
                thread_list[position] = Thread(target=send_to_server, args=(clientSocket, (SERVER_LIST[position],SERVER_PORT), cur_seq_num, segment_list, time_list, position, lock))
                segment_list[position] = None
                thread_list[position].start()
                thread_list[position].join()
            elif (len(set(segment_list)) == 1) and ((set(segment_list)).pop() == cur_seq_num + 1):
                break
            else:
                min_segment = min(segment_list)
                position = segment_list.index(min_segment)
                thread_list[position] = Thread(target=send_to_server, args=(clientSocket, (SERVER_LIST[position],SERVER_PORT), cur_seq_num, segment_list, time_list, position, lock))
                segment_list[position] = None
                thread_list[position].start()
                thread_list[position].join()

    print('File sent successfully')
    print('Time taken to send the file')
    print(time_list)

#################################################################################################################################################
print(SERVER_LIST)
start()
