from sys import argv, exit
import socket
from socket import socket, AF_INET, SOCK_DGRAM
from time import time, gmtime, strftime, sleep

# check correct usage
if len(argv) != 3:
	print("usage: python PingClient.py host port")
	exit(1)

# get command line args
host = argv[1]
try:
	port = int(argv[2])
except ValueError:
	print("port number invalid")
	exit(1)

addr = (host,port)
RTT = []
rxtCount = 0

# socket
soc = socket(AF_INET, SOCK_DGRAM)

for seq in range(0,10):
	msg = "PING " + str(seq) + " " + strftime("%H:%M:%S", gmtime()) + " \r\n"

	start = time()
	soc.sendto(msg,addr)
	rec = receive(soc)
	finish = time()
	
	# successful transmission
	if rec != -1:
		rtt = (finish-start)*1000
		print("ping to " + host + ", seq = " + str(seq) + ", rtt = " + str(int(rtt)) + " ms")
		RTT.append(rtt)

	# unsuccessful transmission
	while rec == 1:
		print("ping to " + host + ", seq = " + str(seq) + ", time out, retransmitting")
		rxtCount = rxtCount+1
		start = time()
		soc.sendto(msg,addr)
		rec = receive(soc)
		finish = time()

		if rec != -1:
			rtt = (fin - start) * 1000  # calculate rtt
			print("ping to " + host + ", seq = " + str(seq) + " (RXT), rxt = " + str(int(rtt)) + " ms")
			RTT.append(rtt)

	sleep(1)

# calculate and print statistics
av = int(sum(RTT)/len(RTT))
mini = int(min(RTT))
maxi = int(max(RTT))

print("--- " + host + " ping statistics ---")
print("10 packets transmitted, " +  str(rxtCount) + " packets retransmitted")
print("rtt min/avg/max = " + str(mini) + "ms " + str(av)  + "ms " + str(maxi) + "ms")

# function to check if message in 1 second
def receive(sock):
    BUFSIZE = 1024
    sock.settimeout(1)
    
    try:
        rec = sock.recvfrom(BUFSIZE)
    except:
        rec = -1
   
    sock.settimeout(0)
    return rec

