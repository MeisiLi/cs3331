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
    global sender_pDrop, sender_pDuplicate, sender_pCorrupt, sender_pOrder
    global sender_maxOrder
    global sender_pDelay
    global sender_maxDelay


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
    # transferFile(receiver, receiver_host, receiver_port, sender_mss, sender_mws, context)
    transfer(receiver, receiver_host, receiver_port, sender_mss, sender_mws, context, sender_gamma)


    # four-segment termination
    termination(receiver, receiver_host, receiver_port, context)
    if(test_terminate): print "terminate done"

def PLD(receiver, receiver_host, receiver_port, packet, rand_num):
    global s_seg_trans
    global s_seg_pld, s_seg_drop, s_seg_corr, s_seg_dup, s_seg_rord, s_seg_dely, s_seg_retr, s_fastretr, s_dup_ack

    error = 0

    if(rand_num < sender_pDrop):
        print "drop"
        s_seg_pld += 1
        s_seg_trans += 1
        s_seg_drop += 1
        sendLog("drop", "D", packet, s_logTime)
        error = EDROP
    elif(rand_num < sender_pDuplicate):
        print "duplicate"
        s_seg_pld += 1
        s_seg_trans += 1
        s_seg_dup += 1
        receiver.sendto(str(packet), (receiver_host, receiver_port))
        sendLog("snd", "D", packet, s_logTime)

        s_seg_pld += 1
        s_seg_trans += 1
        s_seg_dup += 1
        receiver.sendto(str(packet), (receiver_host, receiver_port))
        sendLog("snd/dup", "D", packet, s_logTime)

        error = EDUP
    elif(rand_num < sender_pCorrupt):
        print "corrupt"
        s_seg_pld += 1
        s_seg_trans += 1
        s_seg_corr += 1
        # change the bit
        packet = set_checksum(packet, 1)
        receiver.sendto(str(packet), (receiver_host, receiver_port))
        sendLog("snd/corr", "D", pakcet, s_logTime)

        error = ECORR

    elif(rand_num < sender_pDelay):
        print "delay"
        s_seg_pld += 1
        s_seg_trans += 1
        s_seg_dely += 1

        sleep = random.randint(0, sender_maxDelay)
        time.sleep(sleep)

        receiver.sendto(str(packet), (receiver_host, receiver_port))
        sendLog("snd/dely", "D", packet, s_logTime)
        error = EDELAY
    else:
        print "no error"
        s_seg_trans += 1
        receiver.sendto(str(packet), (receiver_host, receiver_port))
        sendLog("snd", "D", packet, s_logTime)
    
    print "send to: ", get_ack_num(packet), get_seq_num(packet)
    return error

                
def transfer(receiver, receiver_host, receiver_port, mss, mws, context, gamma):
    if(test_transmit):  print "transfer file"

    global s_seq_num, s_ack_num
    global estimatedRTT, devRTT, timeInterval
    global s_seg_pld, s_seg_drop, s_seg_corr, s_seg_dup, s_seg_rord, s_seg_dely, s_seg_retr, s_fastretr, s_dup_ack
    s_seq_num = 1
    s_ack_num = 1

    next_seg = 0
    packet = create_packet()
    packet = set_seq_num(packet, 1)
    packet = set_ack_num(packet, 1)

    while(next_seg < len(context)):
        sendTime = time.time()

        recv_ack = get_ack_num(packet)  # init: 1
        recv_seq = get_seq_num(packet)  # init: 1

        oldPacket = packet

        if(recv_seq == s_seq_num and s_seq_num != 1):
            print "duplicate packet receive"

        else: 
            rand_num = random.random()
            if(s_seq_num < recv_ack):
                s_seq_num = recv_ack
            s_ack_num = recv_seq
            data = getData(context, s_seq_num-1, mss)
            packet = dataPacket(data, s_seq_num, s_ack_num)
            print "send seq and ack: ", s_seq_num, s_ack_num, len(data)
            
            error = PLD(receiver, receiver_host, receiver_port, packet, rand_num)

            retransmit = False

        recvTime = time.time()
        
        try:
            if(error != EDROP):
                oldAck = recv_ack
                data, reply = receiver.recvfrom(1024)
                packet = eval(data)
                if(oldAck == get_ack_num(packet)):
                    sendLog("rcv/DA", "A", packet, s_logTime)
                    s_dup_ack += 1
                else:
                    sendLog("rcv", "A", packet, s_logTime)
                print "receive: ", get_ack_num(packet), get_seq_num(packet) 
        except socket.timeout:
            print "timeout, retranmit"
            receiver.sendto(str(packet), (receiver_host, receiver_port))
            sendLog("snd/RXT", "D", packet, s_logTime)
            s_seg_retr += 1
            retransmit = 1

        if(retransmit == False):
            sampleRTT = recvTime - sendTime
            diff = abs(sampleRTT - estimatedRTT)
            devRTT = 0.75 * devRTT + 0.25 * diff
            estimatedRTT = 0.875 * estimatedRTT + 0.125 * sampleRTT
            timeInterval = estimatedRTT + gamma * devRTT
            receiver.settimeout(timeInterval)

        next_seg = s_seq_num
        
    
        
def getData(context, index, mss):
    message = ""
    l = 0
    if(index + mss < len(context)):
        message = context[index:index+mss]
    else:
        message = context[index:]
    return message

def dataPacket(data, seqNum, ackNum):
    p = create_packet()
    p = set_data_flag(p)
    p = set_data(p, data)
    p = set_seq_num(p, seqNum)
    p = set_ack_num(p, ackNum)
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


    # s_seg_trans += s_seg_retr
    # s_seg_pld += s_seg_retr
    
    final_send(len(context) - 1, s_seg_trans+s_seg_retr, s_seg_pld+s_seg_retr, s_seg_drop, s_seg_corr, s_seg_dup, s_seg_rord, s_seg_dely, s_seg_retr, s_fastretr, s_dup_ack)
    check_state(END_TERMINATE)
    sender_state = NO_CONNECTION

def check_state(state):
    if(state != sender_state):
        sys.exit("current state " + str(sender_state) + " != the needed state " + str(state))


if __name__ == "__main__":
    main()


