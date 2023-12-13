# Attribution: this assignment is based on ICMP Traceroute Lab from Computer Networking: a Top-Down Approach by Jim Kurose and Keith Ross. 
# It was modified for use in CSC249: Networks at Smith College by R. Jordan Crouser in Fall 2022

from socket import * #everything is imported
from ICMPpinger import checksum
import os
import sys
import struct
import time
import select
import binascii

ICMP_ECHO_REQUEST = 8
MAX_HOPS = 30
TIMEOUT = 2.0
TRIES = 2

# The packet that we shall send to each router along the path is the ICMP echo
# request packet, which is exactly what we had used in the ICMP ping exercise.
# We shall use the same packet that we built in the Ping exercise
def build_packet():
    # In the sendOnePing() method of the ICMP Ping exercise, firstly the header of our
    # packet to be sent was made, secondly the checksum was appended to the header and
    # then finally the complete packet was sent to the destination.

    #---------------#
    # Fill in start #
    #---------------#

        # TODO: Make the header in a similar way to the ping exercise.
        # Append checksum to the header.
        # Solution can be implemented in 10 lines of Python code.

        #-----------------------BEGIN-ATTEMPT-1------------------------#
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    myChecksum = 0
    
    ID = os.getpid() & 0xFFFF # Return the current process i 

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

    # construct the final header, with the previously calculated checksum
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1) 
        #-------------------------END-ATTEMPT-1------------------------#
        
    #-------------#
    # Fill in end #
    #-------------#

    # Don’t send the packet yet , just return the final packet in this function.
    packet = header + data
    return packet

def get_route(hostname):
    timeLeft = TIMEOUT
    for ttl in range(1,MAX_HOPS):
        for tries in range(TRIES):
            destAddr = gethostbyname(hostname)

            #---------------#
            # Fill in start #
            #---------------#

                # TODO: Make a raw socket named mySocket
                # Solution can be implemented in 2 lines of Python code.

            #-----------------------BEGIN-ATTEMPT-1------------------------#
            icmp = getprotobyname("icmp")
            mySocket = socket(AF_INET, SOCK_RAW, icmp)
            #-------------------------END-ATTEMPT-1------------------------#

            #-------------#
            # Fill in end #
            #-------------#

            mySocket.setsockopt(IPPROTO_IP, IP_TTL, struct.pack('I', ttl))
            mySocket.settimeout(TIMEOUT)

            try:
                d = build_packet()
                mySocket.sendto(d, (hostname, 0))
                t= time.time()
                startedSelect = time.time()
                
                #-----troubleshoot-----
                #print(timeLeft)
                timeLeft = max(0, timeLeft)
                #---------------------

                whatReady = select.select([mySocket], [], [], timeLeft)
                howLongInSelect = (time.time() - startedSelect)

                if whatReady[0] == []: # Timeout
                    print(" * * * Request timed out.")

                #print("before receive")
                recvPacket, addr = mySocket.recvfrom(1024)
                timeReceived = time.time()
                timeLeft = timeLeft - howLongInSelect

                if timeLeft <= 0:
                    print(" * * * Request timed out.")



            #-----troubleshoot-----
            # the select is timing out --> try a printout of timeleft before select.select
            # exception socket.timeout is a deprecated alias of TimeoutError     
            except timeout:
               #print("In except handeler")
               continue

            else:
                #---------------#
                # Fill in start #
                #---------------#

                    #TODO: Fetch the icmp type from the IP packet
                    # Solution can be implemented in 2 lines of Python code.

                #-----------------------BEGIN-ATTEMPT-1------------------------#
                types, _, _, _, _ = struct.unpack("bbHHh",recvPacket[20:28])
                #-------------------------END-ATTEMPT-1------------------------#


                #-------------#
                # Fill in end #
                #-------------#
                
                if types == 11:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 +bytes])[0]
                    print(" %d rtt=%.0f ms %s" %(ttl, (timeReceived -t)*1000, addr[0]))

                elif types == 3:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    print(" %d rtt=%.0f ms %s" %(ttl, (timeReceived-t)*1000, addr[0]))

                elif types == 0:
                    bytes = struct.calcsize("d")
                    timeSent = struct.unpack("d", recvPacket[28:28 + bytes])[0]
                    print(" %d rtt=%.0f ms %s" %(ttl, (timeReceived - timeSent)*1000, addr[0]))
                    return

                else:
                    print("error")

                break

            finally:
                mySocket.close()

# Runs program
if __name__ == "__main__":
    #target = sys.argv[1]
    #target = sys.argv[0]
    #target = "130.111.46.127"
    #get_route(sys.argv[0])
    #get_route("130.111.46.127")

    addressList = ["130.111.46.127","169.236.10.214",
                   "54.83.192.228", "54.163.225.50",
                   "151.101.118.133", "128.232.132.8",
                   "104.17.118.46", "103.6.198.52",
                   "104.17.192.191", "18.239.168.110"]

    for add in addressList:
        get_route(add)




