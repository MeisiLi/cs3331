# COMP3331 Assignment 
# STP over UDP
# Meisi Li - z5119623
# 9/25/2018 
# receiver.py 

import sys, socket, time, datetime
from globalVal import *

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

    if(is_syn(packet) and get_seq_num(packet) == 0 and get_ack_num(packet) == 0):
        # SYN+ACK packet - handshake #2
        p = create_packet()
        p = set_syn_flag(p)
        p = set_ack_flag(p)
        p = set_ack_num(p, 1)
        p = set_seq_num(p, 0)

        receiver.sendto(str(p), (sender_host, sender_port))
        receiver_state = START_CONNECT

def handshake_connect(packet, receiver):
    global receiver_state

    if(is_ack(packet) and get_seq_num(packet) == 1 and get_ack_num(packet) == 1):
        receiver_state = IN_CONNECTION

def connection(p, receiver, sender_host, sender_port, filename):
    global receiver_state, r_ack_num
    global mess

    # data packet 
    if(is_data(p)):
        data = mess
        if(get_seq_num(p) == r_ack_num):
            r_ack_num = get_seq_num(p) + len(get_data(p))
            data += get_data(p)

        p = create_packet()
        p = set_ack_flag(p)
        p = set_ack_num(p, r_ack_num)

        receiver.sendto(str(p), (sender_host, sender_port))
        mess = data

    # first fin 
    if(is_fin(p)):
        f = open(filename, 'wb')
        f.write(mess)
        f.close()
        r_ack_num = 0
        # return ACK packet 
        p = create_packet()
        p = set_ack_flag(p)

        receiver.sendto(str(p), (sender_host, sender_port))

        # create FIN packet
        p = create_packet()
        p = set_fin_flag(p)

        receiver.sendto(str(p), (sender_host, sender_port))
        receiver_state = START_TERMINATE


    

def termination(packet):
    global receiver_state 
    
    # second fin 
    if(is_ack(packet) and (not is_syn(packet)) and (not is_fin(packet)) and (not is_data(packet))):
        receiver_state = NO_CONNECTION


if __name__ == "__main__":
    main()



