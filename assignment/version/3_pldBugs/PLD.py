# COMP3331 Assignment 
# STP over UDP
# Meisi Li - z5119623
# 9/25/2018 
# LDP.py 

import sys, socket, time, datetime, random
from globalVal import *
from logText import *
from sender import *

def PLD(receiver, receiver_host, receiver_port, mss, mws, context, logTime):
    global s_fileLen
    global s_seg_trans

    if(test_transmit):  print "PLD transfer"

    global s_ack_num, s_seq_num

    transfer = True
    lastSent = 0
    lastAck = 0

    # empty packet 
    p = create_packet()
    
    while(transfer):
        unack_packet = 0
        while((lastSent - lastAck) < mws and lastSent < len(context)):
            rand_num = random.random()
            print "rand: ", rand_num

            data = getData(context, lastSent, mss)
            # send data packets
            p = dataPacket(data, lastSent)
            lastSent = getLen(context, lastSent, mss)
            if(test_transmit):  print "send seq: ", get_seq_num(p)
            receiver.sendto(str(p), (receiver_host, receiver_port))
            s_seg_trans += 1
            sendLog("snd", "D", p, logTime)
            unack_packet += 1

        # receive ack packet 
        try:
            for j in range(unack_packet):
                data, reply = receiver.recvfrom(1024)
                p = eval(data)
                sendLog("rcv", "A", p, logTime)
            if(is_ack(p)):
                tmpAck = get_ack_num(p)
                if(test_transmit): print "get ack ", tmpAck
                if(tmpAck == len(context)):
                    transfer = False
                    s_seq_num = tmpAck
                else:
                    s_seq_num = tmpAck
                    lastSent = tmpAck
                    lastAck = tmpAck
        except socket.timeout:
            sys.exit("transfer fail - timeout")



