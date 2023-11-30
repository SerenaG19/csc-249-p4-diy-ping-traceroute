# Attribution: this assignment is based on ICMP Pinger Lab from Computer Networking: a Top-Down Approach by Jim Kurose and Keith Ross. 
# It was modified for use in CSC249: Networks at Smith College by R. Jordan Crouser in Fall 2022, and by Brant Cheikes for Fall 2023.

from socket import * 
import os
import sys 
import struct 
import time 
import select 
import binascii


ICMP_ECHO_REQUEST = 8

# -------------------------------------
# This method takes care of calculating
#   a checksum to make sure nothing was
#   corrupted in transit.
#  
# You do not need to modify this method
# -------------------------------------
def checksum(string): 
    csum = 0
    countTo = (len(string) // 2) * 2 
    count = 0

    while count < countTo: 
        thisVal = ord(string[count+1]) * 256 + ord(string[count]) 
        csum = csum + thisVal
        csum = csum & 0xffffffff 
        count = count + 2

    if countTo < len(string):
        csum = csum + ord(string[len(string) - 1]) 
        csum = csum & 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff) 
    csum = csum + (csum >> 16)

    answer = ~csum

    answer = answer & 0xffff
 
    answer = answer >> 8 | (answer << 8 & 0xff00) 
    return answer


def receiveOnePing(mySocket, ID, timeout, destAddr): 
    
    timeLeft = timeout
    
    while True:
        # store time at which we begin the select method
        startedSelect = time.time()

        # select.select() documentation: https://docs.python.org/3/library/select.html 
        whatReady = select.select([mySocket], [], [], timeLeft) 

        # calculate time it takes to select
        howLongInSelect = (time.time() - startedSelect)
        if whatReady[0] == []: # Timeout 
            return "Request timed out."

        # store ttime at which the ping was received
        timeReceived = time.time()
        recPacket, addr = mySocket.recvfrom(1024) # receives the packet from the raw socket

        #---------------#
        # Fill in start #
        #---------------#

            # TODO: Fetch the ICMP header from the IP packet
            # Soluton can be implemented in 6 lines of Python code.

            # Notes:
            # "Really need to look at other code BEFORE you fill this in."
            # Need to figure out how / where to find ICMP header from the packet
            # Reverse-engineer the send operation

            # Ideas:
            # Extract header using known set length from the beginning of the packet.
            # From below: type (8), code (8), checksum (16), id (16), sequence (16)

            # Note: mySocket.recvfrom(1024) Returns a bytes object read from an UDP socket and the address of the client socket as a tuple.
        header = recPacket[0:39] # extract header from packet
        #print(header)      
        # IS THIS CORRECT?
        # print(timeLeft)
        # print(timeReceived)
        # print(howLongInSelect)
        delay = howLongInSelect # put it in ms
        #delay = timeReceived - howLongInSelect
        if timeLeft > 0:
                return delay

            # Question: Should this code return the delay? but then wouldn't that prevent the rest of the method from running?
            # Other question: Is info needed to calculate RTT embedded in packet structure? See line 11

            # TODO - verify from ID that the reply you look at is from myID && pull out the time from the message body. one of six lines is a print
            # TODO look at trace in Wireshark
        #-------------#
        # Fill in end #
        #-------------#

        timeLeft = timeLeft - howLongInSelect 
        
        if timeLeft <= 0:
            return "Request timed out."

def sendOnePing(mySocket, destAddr, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    myChecksum = 0

    # Make a dummy header with a 0 checksum
 
    # struct -- Interpret strings as packed binary data
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1) 
    data = struct.pack("d", time.time())

    # Calculate the checksum on the data and the dummy header. 
    myChecksum = checksum(''.join(map(chr, header+data)))

    # Get the right checksum, and put in the header 
    if sys.platform == 'darwin':
        # Convert 16-bit integers from host to network byte order 
        myChecksum = htons(myChecksum) & 0xffff
    else:
        myChecksum = htons(myChecksum)

    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1) 
    packet = header + data

    mySocket.sendto(packet, (destAddr, 1)) # AF_INET address must be tuple, not str 
    # Both LISTS and TUPLES consist of a number of objects
    # which can be referenced by their position number within the object.

def doOnePing(destAddr, timeout): 
    icmp = getprotobyname("icmp")

    # SOCK_RAW is a powerful socket type. For more details:	http://sock-raw.org/papers/sock_raw
    mySocket = socket(AF_INET, SOCK_RAW, icmp)

    myID = os.getpid() & 0xFFFF # Return the current process i 
    sendOnePing(mySocket, destAddr, myID)
    delay = receiveOnePing(mySocket, myID, timeout, destAddr)
 
    mySocket.close() 
    return delay

def ping(host, timeout=1, repeat=3):

    # timeout=1 means: If one second goes by without a reply from the server,
    # the client assumes that either the client's ping or the server's pong is lost 
    dest = gethostbyname(host)
    print(f"Pinging {host} [{dest}] {repeat} times using Python:")

    # Send ping requests to a server separated by approximately one second 
    # Do this only a fixed number of times as determined by 'repeat' argument
    numPings = 1
    while (numPings <= repeat) :
        delay = doOnePing(dest, timeout) 
        print(f"Ping {numPings} RTT {delay} sec")
        time.sleep(1) # one second 
        numPings += 1
    return delay

# Runs program
if __name__ == "__main__":
    # get target address from command line
    #target = sys.argv[1]
    target = "8.8.8.8"
    ping(target)
