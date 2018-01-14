import sys
import os
from struct import *
from socket import *
from random import *

#import sys

#sys.setrecursionlimit(300000000)

SERVER_PORT = int(sys.argv[1])
FILE_NAME = sys.argv[2]
PROBABILITY = float(sys.argv[3])

def probabily_loss():
    tmp = int(abs(PROBABILITY*100))
    if randint(1,100) in range(1, tmp+1):
        return True
    return False

def get_ack_segment(next_seq_num):
    if(next_seq_num != 0):
        ack_segment_format = Struct('I H H')
        ack_segment_identifier = 43690
        return ack_segment_format.pack(next_seq_num, ack_segment_identifier, 0)
    else:
        return

def carry_around_add(a, b):
    c = a + b
    return (c & 0xffff) + (c >> 16)

def validate_checksum(data, received_checksum):
    checksum_value = 0
    for i in range(0, len(data), 2):
        #i = ord(i[0])<<8 | ord(i[1])
        if(i == (len(data)-1)):
            break
        i = ord(data[i]) + (ord(data[i+1]) << 8)
        checksum_value = carry_around_add(checksum_value,i)
    if((checksum_value & received_checksum) == 0):
        return True
    else:
        return False

def parse_data_segment(segment, current_segment):
    segment_length = len(segment) - 8
    segment_format = Struct('I H H {}'.format(str(segment_length) + 's'))
    segment_identifier = 21845

    unpacked_data = segment_format.unpack(segment)
    #print(unpacked_data)
    segment_seq_num = unpacked_data[0]
    if segment_seq_num < current_segment:
        return current_segment
    if probabily_loss():
        print('Packet loss, sequence number = ' + str(segment_seq_num))
        return 0
    if((segment_identifier == unpacked_data[1]) and validate_checksum((unpacked_data[3]).decode('utf-8'), unpacked_data[2])):
        #write to file
        f = open( FILE_NAME , 'a')
        f.write((unpacked_data[3]).decode('utf-8'))
        f.close()
        return segment_seq_num + 1
    else:
        return segment_seq_num

def start():
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind((gethostbyname(gethostname()), SERVER_PORT))
    #The above statement does not work properly on Mac
    #serverSocket.bind(('', SERVER_PORT))
    print ('The server is ready to receive')
    current_segment = 0
    while 1:
        message, clientAddress = serverSocket.recvfrom(2048)
        tmp = parse_data_segment(message, current_segment)
        if tmp != 0:
            current_segment = tmp
        ack = get_ack_segment(tmp)
        if ack:
            serverSocket.sendto(ack, clientAddress)
####################################################################################################################################################
start()
