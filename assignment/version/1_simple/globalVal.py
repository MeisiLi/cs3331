# COMP3331 Assignment 
# STP over UDP
# Meisi Li - z5119623
# 9/25/2018 
# global.py - global variable

from packet import *

# debug 
test_start          = True
test_correct        = True
test_connection     = True
test_handshake      = True
test_transmit       = False
test_ackseq         = True
test_terminate      = True

# different state 
NO_CONNECTION       = 0
START_CONNECT       = 1
IN_CONNECTION       = 2
START_TERMINATE     = 3
END_TERMINATE       = 4
RETRANSMITION       = 5

# ============================================== sender ================================================
# initial value of EstimatedRTT and DevRTT
EstimatedRTT        = 500 # in millisecond
DevRTT              = 250 # in millisecond 

# global variable 
sender_state        = NO_CONNECTION
SampleRTT           = 0
s_ack_num           = 0 
s_seq_num           = 0 


# ============================================ receiver ==================================================
# global variable 
receiver_state      = NO_CONNECTION
r_ack_num           = 0 
r_seq_num           = 0 
mess                = ""

