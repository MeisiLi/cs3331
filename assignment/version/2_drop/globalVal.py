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
test_seg_trans      = False

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

s_fileLen             = 0

# number of segments
s_seg_trans = 0
s_seg_pld   = 0
s_seg_drop  = 0
s_seg_corr  = 0
s_seg_dup   = 0
s_seg_rord  = 0
s_seg_dely  = 0
s_seg_retr  = 0
s_fastretr  = 0
s_dup_ack   = 0

# initial log time
s_logTime     = 0

# ============================================ receiver ==================================================
# global variable 
receiver_state      = NO_CONNECTION
r_ack_num           = 0 
r_seq_num           = 0 
mess                = ""

r_fileLen           = 0

# number 
r_seg_total     = 0
r_seg_data      = 0
r_seg_bitError  = 0
r_seg_dup_data  = 0
r_seg_dup_ack   = 0

# inital log time
logTime = 0

