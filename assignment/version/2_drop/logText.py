# COMP3331 Assignment 
# STP over UDP
# Meisi Li - z5119623
# 9/25/2018 
# logText.py 

import sys, socket, time, datetime, random
from globalVal import *

def sendLog(event, packetType, p, logtime):
    
    currTime = time.clock() * 1000
    if(packetType == "S"):
        logtime = currTime
    # print "logtime and currTime:  ", logtime, currTime
    currTime = str(currTime - logtime)

    seq = str(get_seq_num(p))
    ack = str(get_ack_num(p))
    
    buf = str(0)

    if(is_data(p)):
        buf = str(len(get_data(p)))

    # logFormat = [event, time, packetType, seq, buf, ack]

    text = event + "\t\t" + currTime + "\t\t" + packetType + "\t\t" + seq + "\t" + buf + "\t" + ack + "\n"
    # text = event + "\t\t" + currTime + "\n"

    f = open("Sender_log.txt", 'a+')
    f.write(text)
    f.close()

    return logtime

def recvLog(event, packetType, p, logtime):
    
    currTime = time.clock() * 1000
    if(packetType == "S"):
        logtime = currTime
    # print "logtime and currTime:  ", logtime, currTime
    currTime = str(currTime - logtime)

    seq = str(get_seq_num(p))
    ack = str(get_ack_num(p))
    
    buf = str(0)

    if(is_data(p)):
        buf = str(len(get_data(p)))

    # logFormat = [event, time, packetType, seq, buf, ack]

    text = event + "\t\t" + currTime + "\t\t" + packetType + "\t\t" + seq + "\t" + buf + "\t" + ack + "\n"
    # text = event + "\n"

    f = open("Receiver_log.txt", 'a+')
    f.write(text)
    f.close()

    return logtime

def final_send(fileLen, n1, n2, n3, n4, n5, n6, n7, n8, n9, n10):
    f = open("Sender_log.txt", 'a+')
    f.write("===================================================\n")
    
    f.write("Size of the file (in Bytes)                    " + str(fileLen) + "\n")
    f.write("Segments transmitted (including drop & RXT)    " + str(n1) + "\n")
    f.write("Number of Segments handled by PLD              " + str(n2) + "\n")
    f.write("Number of Segments dropped                     " + str(n3) + "\n")
    f.write("Number of Segments Corrupted                   " + str(n4) + "\n")
    f.write("Number of Segments Re-ordered                  " + str(n5) + "\n")
    f.write("Number of Segments Duplicated                  " + str(n6) + "\n")
    f.write("Number of Segments Delayed                     " + str(n7) + "\n")
    f.write("Number of Retransmissionns due to TIMEOUT      " + str(n8) + "\n")
    f.write("Number of FAST RETRANSMISSION                  " + str(n9) + "\n")
    f.write("Number of DUP ACKS received                    " + str(n10) + "\n")

    f.write("===================================================\n")

def final_recv(fileLen, n1, n2, n3, n4, n5):

    f = open("Receiver_log.txt", 'a+')
    f.write("===================================================\n")
    
    f.write("Amount of data received (bytes)                " + str(fileLen) + "\n")
    f.write("Total Segments Received                        " + str(n1) + "\n")
    f.write("Data segments received                         " + str(n2) + "\n")
    f.write("Data segments with Bit Errors                  " + str(n3) + "\n")
    f.write("Duplicate data segments received               " + str(n4) + "\n")
    f.write("Duplicate ACKs sent                            " + str(n5) + "\n")

    f.write("===================================================\n")


