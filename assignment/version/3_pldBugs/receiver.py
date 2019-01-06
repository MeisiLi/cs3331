# COMP3331 Assignment 
# STP over UDP
# Meisi Li - z5119623
# 9/25/2018 
# receiver.py 

import sys, socket, time, datetime
from globalVal import *
from logText import *

def main():
    global receiver_state
    global ack_num, seq_num
    global mess

    if(test_start): print "receiver start"

    # checking input argument ... 
    if(len(sys.argv) != 3):
        sys.exit("usage: python receiver.py <receiver port> <filename>")

    if(not (sys.argv[1].isdigit())):
        sys.exit("usage: python receiver.py <receiver port> <filename>")
        
    # getting input variable ... 
    receiver_host   = "localhost"
    receiver_port   = int(sys.argv[1])
    filename        = sys.argv[2]

    if(test_correct):
        print (receiver_host + " " + str(receiver_port) + " " + filename)

    # create socket - Intenet, UDP
    receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 
    receiver.bind((receiver_host, receiver_port))
    if(test_start): print "create socket"


    while True:
        data, sender = receiver.recvfrom(1024)
        p = eval(data)

        sender_host = sender[0]
        sender_port = sender[1]
        
        # reply the second packet 
        if(receiver_state == NO_CONNECTION):
            # reset file 
            f = open("Receiver_log.txt", 'w')
            f.close()
            establish_handshake(p, receiver, sender_host, sender_port)
            if(test_handshake): print "handshake setting up..."

        # handshake finish 
        elif(receiver_state == START_CONNECT):
            handshake_connect(p, receiver)
            if(test_handshake): print "handshake done"
            mess = ""

        # transmit data 
        elif(receiver_state == IN_CONNECTION):
            connection(p, receiver, sender_host, sender_port, filename)
    
        elif(receiver_state == START_TERMINATE):
            termination(p)
            if(test_terminate): print "termination done"
    

def establish_handshake(packet, receiver, sender_host, sender_port):
    global receiver_state 
    global logTime 

    if(is_syn(packet) and get_seq_num(packet) == 0 and get_ack_num(packet) == 0):
        logTime = recvLog("rcv", "S", packet, logTime)
        # SYN+ACK packet - handshake #2
        p = create_packet()
        p = set_syn_flag(p)
        p = set_ack_flag(p)
        p = set_ack_num(p, 1)
        p = set_seq_num(p, 0)

        receiver.sendto(str(p), (sender_host, sender_port))
        recvLog("snd", "SA", p, logTime)
        receiver_state = START_CONNECT

def handshake_connect(packet, receiver):
    global receiver_state, r_ack_num, r_seq_num

    if(is_ack(packet) and get_seq_num(packet) == 1 and get_ack_num(packet) == 1):
        recvLog("rcv", "A", packet, logTime)
        receiver_state = IN_CONNECTION
        r_ack_num = 1
        r_seq_num = 1

def connection(p, receiver, sender_host, sender_port, filename):
    global receiver_state, r_ack_num, r_seq_num
    global mess
    global nextSeqNum

    # data packet 
    if(is_data(p)):
        send_ack = get_ack_num(p)
        send_seq = get_seq_num(p)
        recv_data = get_data(p)
        print "receive: ", send_ack, send_seq, len(recv_data) 
        # checksum 
        calChecksum = getChecksum()
        iniChecksum = get_checksum(p)
        if(calChecksum != iniChecksum):
            print "corrupt packet"
        elif(send_seq != r_ack_num):
            print "duplicate", send_seq, r_ack_num
            p = create_packet()
            p = set_ack_flag(p)
            p = set_seq_num(p, r_seq_num)
            p = set_ack_num(p, r_ack_num)
            receiver.sendto(str(p), (sender_host, sender_port))
            recvLog("snd/DA", "A", p, logTime)
            print "sendto: ", r_seq_num, r_ack_num
        else:
            data = mess

            r_seq_num = send_ack
            r_ack_num = send_seq + len(recv_data)
            data += recv_data
            print "check again: ", send_ack, send_seq, len(recv_data) 
            print "check recv: ", r_seq_num, r_ack_num, len(recv_data) 
            

            recvLog("rcv", "D", p, logTime)

            p = create_packet()
            p = set_ack_flag(p)
            p = set_seq_num(p, send_ack)
            p = set_ack_num(p, r_ack_num)

            receiver.sendto(str(p), (sender_host, sender_port))
            print "sendto: ", get_ack_num(p), get_seq_num(p) 
            recvLog("snd", "A", p, logTime)
            mess = data

    # first fin 
    if(is_fin(p)):
        recvLog("rcv", "F", p, logTime)
        f = open(filename, 'wb')
        f.write(mess)
        f.close()
        # r_ack_num = 0
        # return ACK packet
        send_ack = get_ack_num(p)
        send_seq = get_seq_num(p)

        r_ack_num = send_seq + 1
        r_seq_num = send_ack

        p = create_packet()
        p = set_ack_flag(p)
        p = set_seq_num(p, send_ack)
        p = set_ack_num(p, send_seq+1)

        receiver.sendto(str(p), (sender_host, sender_port))
        recvLog("snd", "A", p, logTime)

        # create FIN packet
        p = create_packet()
        p = set_fin_flag(p)
        p = set_ack_num(p, send_seq+1)
        p = set_seq_num(p, send_ack)

        receiver.sendto(str(p), (sender_host, sender_port))
        recvLog("snd", "F", p, logTime)
        receiver_state = START_TERMINATE

        r_ack_num = 0
        r_seq_num = 0

def getChecksum():
    return 0
    

def termination(packet):
    global receiver_state 
    
    # second fin 
    if(is_ack(packet) and (not is_syn(packet)) and (not is_fin(packet)) and (not is_data(packet))):
        recvLog("rcv", "A", packet, logTime)
        final_recv(len(mess)-1, r_seg_total, r_seg_data, r_seg_bitError, r_seg_dup_data, r_seg_dup_ack)
        receiver_state = NO_CONNECTION


if __name__ == "__main__":
    main()



