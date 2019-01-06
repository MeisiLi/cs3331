# COMP3331 Assignment 
# STP over UDP
# Meisi Li - z5119623
# 9/25/2018 
# sender.py 

import sys, socket, time, datetime, random
from globalVal import *

def main():
    # change the sender_state variable 
    global sender_state
    global ack_num, seq_num

    if(test_start): 
        print "sender start ... "

    # checking input argument ... 
    if(len(sys.argv) != 15):
        sys.exit("usage: python receiver.py <receiver_host_ip> <receiver_port> <filename> <MWS> <MSS> <gamma> <pDrop> <pDuplicate> <pCorrupt> <pOrder> <maxOrder> <pDelay> <maxDelay> <seed>")

    if(not sys.argv[2].isdigit()) and (not sys.argv[4].isdigit()) and (not sys.argv[5].isdigit()): 
        sys.exit("usage: python receiver.py <receiver_host_ip> <receiver_port> <filename> <MWS> <MSS> <gamma> <pDrop> <pDuplicate> <pCorrupt> <pOrder> <maxOrder> <pDelay> <maxDelay> <seed>")
        
    # getting input variable ... 
    receiver_host       = sys.argv[1]
    receiver_port       = int(sys.argv[2])
    filename            = sys.argv[3]
    sender_mws          = int(sys.argv[4])
    sender_mss          = int(sys.argv[5])
    sender_gamma        = float(sys.argv[6])
    sender_pDrop        = float(sys.argv[7])
    sender_pDuplicate   = float(sys.argv[8])
    sender_pCorrupt     = float(sys.argv[9])
    sender_pOrder       = float(sys.argv[10])
    sender_maxOrder     = float(sys.argv[11])
    sender_pDelay       = float(sys.argv[12])
    sender_maxDelay     = float(sys.argv[13])
    sender_seed         = int(sys.argv[14])

    # random
    rand_seed = random.seed(sender_seed)
    rand_num = random.random()
    print "rand: ", rand_seed, rand_num

    # create socket 
    receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if(test_start): print "create socket"

    # three-handshake connection 
    three_handshake(receiver, receiver_host, receiver_port)
    if(test_handshake): print "handshake done"
    
    # file trasmittion
    transferFile(receiver, receiver_host, receiver_port, filename, sender_mss, sender_mws)

    # four-segment termination
    termination(receiver, receiver_host, receiver_port)
    if(test_terminate): print "terminate done"


def transferFile(receiver, receiver_host, receiver_port, filename, mss, mws):
    if(test_transmit):  print "file transfer"
    f = open(filename, 'rb')
    context = f.read()

    global s_ack_num, s_seq_num
    s_ack_num = 0
    s_seq_num = 0

    transfer = True
    lastSent = 0
    lastAck = 0

    while(transfer):
        i = 0
        while((lastSent - lastAck) < mws and lastSent < len(context)):
            data = getData(context, lastSent, mss)
            # send data packets
            p = dataPacket(data, lastSent)
            lastSent = getLen(context, lastSent, mss)
            if(test_transmit):  print "send seq: ", get_seq_num(p)
            receiver.sendto(str(p), (receiver_host, receiver_port))
            i += 1

        # receive ack packet 
        try:
            for j in range(i):
                data, reply = receiver.recvfrom(1024)
            p = eval(data)
            if(is_ack(p)):
                tmpAck = get_ack_num(p)
                if(test_transmit): print "get ack ", tmpAck
                if(tmpAck == len(context)):
                    transfer = False
                else:
                    s_seq_num = tmpAck
                    lastSent = tmpAck
                    lastAck = tmpAck
        except socket.timeout:
            sys.exit("transfer fail - timeout")

        
def getData(context, index, mss):
    message = ""
    l = 0
    if(index + mss < len(context)):
        message = context[index:index+mss]
    else:
        message = context[index:]
    return message

def dataPacket(data, seqNum):
    p = create_packet()
    p = set_data_flag(p)
    p = set_data(p, data)
    p = set_seq_num(p, seqNum)
    return p

def getLen(context, index, mss):
    l = 0
    if(index + mss < len(context)):
        l = index+mss
    else:
        l = len(context)
    return l


def three_handshake(receiver, receiver_host, receiver_port):
    # change the sender_state variable 
    global sender_state

    check_state(NO_CONNECTION)

    # SYN packet send - handshake #1
    p = create_packet()
    p = set_syn_flag(p)
    p = set_seq_num(p, 0)

    receiver.sendto(str(p), (receiver_host, receiver_port))
    sender_state = START_CONNECT

    # receive the SYN+ACK packet - handshake #3
    data, reply = receiver.recvfrom(1024)
    p = eval(data)


    if(is_syn(p) and is_ack(p) and get_seq_num(p) == 0 and get_ack_num(p) == 1):

        p = create_packet()
        p = set_ack_flag(p)
        p = set_seq_num(p, 1)
        p = set_ack_num(p, 1)

        check_state(START_CONNECT)
        receiver.sendto(str(p), (receiver_host, receiver_port))
        sender_state = IN_CONNECTION
    else:
        sys.exit("The handshake broken")

    # checking the connection 
    check_state(IN_CONNECTION)


   
def termination(receiver, receiver_host, receiver_port):
    global sender_state

    check_state(IN_CONNECTION)

    # FIN packet send 
    p = create_packet()
    p = set_fin_flag(p)

    receiver.sendto(str(p), (receiver_host, receiver_port))

    while( sender_state != END_TERMINATE ):
        data, reply = receiver.recvfrom(1024)
        p = eval(data)

        if(is_ack(p) and (not is_syn(p)) and (not is_fin(p)) and (not is_data(p))):
            sender_state = START_TERMINATE

        if(is_fin(p) and (not is_syn(p)) and (not is_ack(p)) and (not is_data(p)) and sender_state == START_TERMINATE):
            # FIN-ACK send 
            p = create_packet()
            p = set_ack_flag(p)

            receiver.sendto(str(p), (receiver_host, receiver_port))
            sender_state = END_TERMINATE


    check_state(END_TERMINATE)
    sender_state = NO_CONNECTION

def check_state(state):
    if(state != sender_state):
        sys.exit("current state " + str(sender_state) + " != the needed state " + str(state))


if __name__ == "__main__":
    main()


