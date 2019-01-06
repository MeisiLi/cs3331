# COMP3331 Assignment 
# STP over UDP
# Meisi Li - z5119623
# 9/25/2018 
# sender.py 

import sys, socket, time, datetime, random
from globalVal import *
from logText import *


def main():
    # change the sender_state variable 
    global sender_state
    global ack_num, seq_num
    global s_logTime

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
    random.seed(sender_seed)

    # create socket 
    receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    if(test_start): print "create socket"

    # reset file
    f = open("Sender_log.txt", 'w')
    f.close()
    
    # get context
    f = open(filename, 'rb')
    context = f.read()
    f.close()


    # three-handshake connection 
    three_handshake(receiver, receiver_host, receiver_port)
    if(test_handshake): print "handshake done"
    
    # file trasmittion
    if(sender_pDrop == 0 and sender_pDuplicate == 0 and sender_pCorrupt == 0 and sender_pOrder == 0 and sender_pDelay == 0):
        transferFile(receiver, receiver_host, receiver_port, sender_mss, sender_mws, context)
    else:
        PLD(receiver, receiver_host, receiver_port, sender_mss, sender_mws, context, sender_pDrop)

    # four-segment termination
    termination(receiver, receiver_host, receiver_port, context)
    if(test_terminate): print "terminate done"

def PLD(receiver, receiver_host, receiver_port, mss, mws, context, pdrop):
    global s_fileLen
    global s_seg_trans, s_seg_drop, s_seg_pld, seg_retr

    if(test_transmit):  print "PLD - file transfer"

    global s_ack_num, s_seq_num

    transfer = True
    lastSent = 0
    lastAck = 0

    # segment flag
    drop = 0
    duplicate = 0
    corrupt = 0
    order = 0
    delay = 0

    is_retransmit = False

    # empty packet 
    p = create_packet()

    while(transfer):
        unack_packet = 0
        while((lastSent - lastAck) < mws and lastSent < len(context)):
            if(duplicate == 0 and (is_retransmit == False)):
                rand_num = random.random()
                print "rand_num: ", rand_num
                if(rand_num < pdrop):
                    drop = 1
                    s_seg_drop += 1

            if(drop == 0):  
            
                data = getData(context, lastSent, mss)
                # send data packets
                p = dataPacket(data, lastSent)
                lastSent = getLen(context, lastSent, mss)
                if(test_transmit):  print "send seq: ", get_seq_num(p)
                receiver.sendto(str(p), (receiver_host, receiver_port))
                event = "snd"
                s_seg_trans += 1
                if(test_seg_trans): print "seg_trans: ", s_seg_trans

                if(is_retransmit):
                    print "retransmit"
                    seg_retr += 1
                    if_retransmit = False
                    event += "\RXT"

                sendLog(event, "D", p, s_logTime)
                unack_packet += 1

            else:   
                p = dataPacket(data, lastSent)
                lastSent = getLen(context, lastSent, mss)
                sendLog("drop", "D", p, s_logTime)
                drop = 0
                

        # receive ack packet 
        for j in range(unack_packet):
            data, reply = receiver.recvfrom(1024)
            p = eval(data)
            if(is_ack(p)):
                sendLog("rcv", "A", p, s_logTime)
                tmpAck = get_ack_num(p)
                if(test_transmit): print "get ack ", tmpAck
                if(tmpAck == len(context)):
                    transfer = False
                    s_seq_num = tmpAck
                else:
                    s_seq_num = tmpAck
                    lastSent = tmpAck
                    lastAck = tmpAck


# when the simple STP (all set to zero and any MSS)
def transferFile(receiver, receiver_host, receiver_port, mss, mws, context):
    global s_fileLen
    global s_seg_trans

    if(test_transmit):  print "file transfer"

    global s_ack_num, s_seq_num

    transfer = True
    lastSent = 0
    lastAck = 0

    # empty packet 
    p = create_packet()

    while(transfer):
        unack_packet = 0
        while((lastSent - lastAck) < mws and lastSent < len(context)):
            data = getData(context, lastSent, mss)
            # send data packets
            p = dataPacket(data, lastSent)
            lastSent = getLen(context, lastSent, mss)
            if(test_transmit):  print "send seq: ", get_seq_num(p)
            receiver.sendto(str(p), (receiver_host, receiver_port))
            s_seg_trans += 1
            sendLog("snd", "D", p, s_logTime)
            if(test_seg_trans): print "seg_trans: ", s_seg_trans
            unack_packet += 1

        # receive ack packet 
        try:
            for j in range(unack_packet):
                data, reply = receiver.recvfrom(1024)
                p = eval(data)
                sendLog("rcv", "A", p, s_logTime)
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
    p = set_ack_num(p, 1)
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
    global s_seq_num, s_ack_num
    global s_seg_trans
    global s_logTime

    check_state(NO_CONNECTION)

    # SYN packet send - handshake #1
    p = create_packet()
    p = set_syn_flag(p)
    p = set_seq_num(p, 0)

    receiver.sendto(str(p), (receiver_host, receiver_port))
    s_logTime = time.clock() * 1000
    s_logTime = sendLog("snd", "S", p, s_logTime)
    s_seg_trans += 1
    if(test_seg_trans): print "seg_trans: ", s_seg_trans
    sender_state = START_CONNECT

    # receive the SYN+ACK packet - handshake #3
    data, reply = receiver.recvfrom(1024)
    p = eval(data)
    sendLog("rcv", "SA", p, s_logTime)


    if(is_syn(p) and is_ack(p) and get_seq_num(p) == 0 and get_ack_num(p) == 1):

        s_seq_num = 1
        s_ack_num = 1

        p = create_packet()
        p = set_ack_flag(p)
        p = set_seq_num(p, 1)
        p = set_ack_num(p, 1)

        check_state(START_CONNECT)
        receiver.sendto(str(p), (receiver_host, receiver_port))
        sendLog("snd", "A", p, s_logTime)
        s_seg_trans += 1
        if(test_seg_trans): print "seg_trans: ", s_seg_trans
        sender_state = IN_CONNECTION
    else:
        sys.exit("The handshake broken")

    # checking the connection 
    check_state(IN_CONNECTION)


   
def termination(receiver, receiver_host, receiver_port, context):
    global sender_state
    global s_seq_num, s_ack_num
    global s_seg_trans

    check_state(IN_CONNECTION)

    # FIN packet send 
    p = create_packet()
    p = set_fin_flag(p)
    p = set_seq_num(p, s_seq_num)
    p = set_ack_num(p, s_ack_num)

    receiver.sendto(str(p), (receiver_host, receiver_port))
    sendLog("snd", "F", p, s_logTime)
    s_seg_trans += 1
    if(test_seg_trans): print "seg_trans: ", s_seg_trans

    while( sender_state != END_TERMINATE ):
        data, reply = receiver.recvfrom(1024)
        p = eval(data)

        if(is_ack(p) and (not is_syn(p)) and (not is_fin(p)) and (not is_data(p))):
            sendLog("rcv", "A", p, s_logTime)
            sender_state = START_TERMINATE

        if(is_fin(p) and (not is_syn(p)) and (not is_ack(p)) and (not is_data(p)) and sender_state == START_TERMINATE):
            sendLog("rcv", "F", p, s_logTime)
            
            recv_ack = get_ack_num(p)
            recv_seq = get_seq_num(p)

            s_seq_num = recv_ack
            s_ack_num = recv_seq + 1

            # FIN-ACK send 
            p = create_packet()
            p = set_ack_flag(p)
            p = set_seq_num(p, recv_ack)
            p = set_ack_num(p, recv_seq+1)

            receiver.sendto(str(p), (receiver_host, receiver_port))
            sendLog("snd", "A", p, s_logTime)
            s_seg_trans += 1
            if(test_seg_trans): print "seg_trans: ", s_seg_trans
            sender_state = END_TERMINATE


    final_send(len(context) - 1, s_seg_trans, s_seg_pld, s_seg_drop, s_seg_corr, s_seg_dup, s_seg_rord, s_seg_dely, s_seg_retr, s_fastretr, s_dup_ack)
    check_state(END_TERMINATE)
    sender_state = NO_CONNECTION

def check_state(state):
    if(state != sender_state):
        sys.exit("current state " + str(sender_state) + " != the needed state " + str(state))


if __name__ == "__main__":
    main()


