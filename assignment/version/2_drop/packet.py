# COMP3331 Assignment 
# STP over UDP
# Meisi Li - z5119623
# 9/25/2018 
# packet.py

# position in packet 
SEQ     = 0
ACK_NUM = 1
DATA    = 6

# flags 
SYN_FLAG    = 3
ACK_FLAG    = 4
FIN_FLAG    = 5
DATA_FLAG   = 2

# create a new packet - header: 
# [seq_num, ack_num, has_data, is_syn, is_ack, is_fin, dataLen]
# timeToLive??
def create_packet():
    packet = [0, 0, 0, 0, 0, 0, 0]
    return packet

# set sequence number 
def set_seq_num(packet, value):
    packet[SEQ] = value
    return packet

# get sequence number 
def get_seq_num(packet):
    return packet[SEQ]

# set acknowledge number
def set_ack_num(packet, value):
    packet[ACK_NUM] = value
    return packet

# get acknowledge number
def get_ack_num(packet):
    return packet[ACK_NUM]

# set flags
def set_syn_flag(packet):
    packet[SYN_FLAG] = 1
    return packet

def set_ack_flag(packet):
    packet[ACK_FLAG] = 1
    return packet

def set_fin_flag(packet):
    packet[FIN_FLAG] = 1
    return packet

def set_data_flag(packet):
    packet[DATA_FLAG] = 1
    return packet

# check flags
def is_syn(packet): 
    res = packet[SYN_FLAG]
    return res == 1

def is_ack(packet): 
    res = packet[ACK_FLAG] 
    return res == 1

def is_fin(packet): 
    res = packet[FIN_FLAG]
    return res == 1

def is_data(packet): 
    res = packet[DATA_FLAG]
    return res == 1

# know what flag is set
def get_flag(packet):
    flag = ""

    if(is_syn(packet)):
        flag += "/syn/"
    if(is_ack(packet)):
        flag += "/ack/"
    if(is_fin(packet)):
        flag += "/fin/"
    if(is_data(packet)):
        flag += "/data/"

    return flag

# set data 
def set_data(packet, data):
    packet[DATA] = data
    return packet

# get data
def get_data(packet):
   return packet[DATA] 

