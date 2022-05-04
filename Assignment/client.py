import socket
from sys import *
import threading
import time
from datetime import datetime

temp_id = None
lock = threading.Condition()

# Check arguments, correct and assign to variables
if len(argv) != 4:
	print("Usage: client.py server_ip server_port client_udp_port")
	exit()
server_ip = argv[1]
server_port = int(argv[2])
client_udp_port = int(argv[3])

def contactlog_delay(tempID):
	# sleep for 120 sec and remove username from list
	time.sleep(120)

	with lock:	
		# get lines from contact_log
		f = open("z5112961_contactlog.txt","r")
		lines = f.readlines()
		f.close()
		# remove correct line from list
		for line in lines:
			if tempID in line:
				lines.remove(line)
				break
		# write new list to file
		f = open("z5112961_contactlog.txt","w")
		for line in lines:
			f.write(line)
		f.close()
		lock.notify()


def central():
	global server_ip
	global server_port
	global client_udp_port

	# set up UDP socket 
	UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
	UDPServerSocket.bind((server_ip, client_udp_port)) 

	# wait for incoming
	while(True):
		beacon = UDPServerSocket.recvfrom(63)
		beacon = beacon[0].split()
		data = beacon[0]+", "+beacon[1]+" "+beacon[2]+", "+beacon[3]+" "+beacon[4]+"."
		tID = beacon[0]

		# get start and expiry time
		start = beacon[1]+" "+beacon[2]
		end = beacon[3]+" "+beacon[4]
		start = datetime.strptime(start, '%d/%m/%Y %H:%M:%S')
		end = datetime.strptime(end, '%d/%m/%Y %H:%M:%S')
		
		# check if curr time is between start and expiry
		curr = datetime.now()
		if curr > start and curr < end:
			# print msg, beacon valid
			print("Recevied beacon:\n"+data)
			print("Current time is: "+curr.strftime("%d/%m/%Y %H:%M:%S"))
			print("The beacon is valid.")
			# store beacon info in z5112961_contactlog.txt
			with lock:
				f = open("z5112961_contactlog.txt","a+")
				f.write(beacon[0]+" "+beacon[1]+" "+beacon[2]+" "+beacon[3]+" "+beacon[4]+"\n")
				f.close()
				lock.notify()
			# set up thread for 3 min removal
			delay_thread=threading.Thread(target=contactlog_delay, args=(tID,))
			delay_thread.daemon=True
			delay_thread.start()
		else:
			# print msg, beacon invalid
			print("Recevied beacon:\n"+data)
			print("Current time is: "+curr.strftime("%d/%m/%Y %H:%M:%S"))
			print("The beacon is invalid.")

def peripheral(cmd):
	global server_ip
	global server_port
	global client_udp_port

	if temp_id == None:
		print("Error: No TempID")
	else:
		try:
			cmd = cmd.split()
			# Create a UDP socket at client side
			serverAddressPort = (cmd[1], int(cmd[2]))
			UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
			# get line to send: "tempID start expiry version"
			info = temp_id
			f = open("tempIDs.txt","r")
			lines = f.readlines()
			f.close()
			for line in lines:
				if temp_id in line:
					l = line
					break

			l = l.split()
			info = temp_id+" "+l[2]+" "+l[3]+" "+l[4]+" "+l[5]+" 1"

			# Send to server using created UDP socket
			UDPClientSocket.sendto(info.encode(), serverAddressPort)
		except:
			print("Error: Invalid command")
# Create a TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Connect the socket to the port where the server is listening
server_address = ('localhost', server_port)
sock.connect(server_address)

# Collect login in details
uname = raw_input("Username: ")
while True:
	pwd = raw_input("Password: ")

	# Send data: "<uname> <pwd>"
	credentials = uname+" "+pwd+"\n"
	sock.sendall(credentials.encode())
	#receive response from server and print appropriate response
	cred_msg = sock.recv(80).decode()
	print(cred_msg)
	if (cred_msg == "Your account is blocked due to multiple login failures. Please try again later"):
		sock.close()
		exit()
	if (cred_msg == "Your account is blocked due to multiple login failures. Please try again later"):
		sock.close()
		exit()
	if (cred_msg == "Welcome to the BlueTrace Simulator!"):
		break

# Create thread to handle central 
central_thread=threading.Thread(target=central)
central_thread.daemon=True
central_thread.start()

# Logged in, wait for command and process
while True:
	cmd = raw_input()
	
	if cmd == "logout":
		sock.sendall(cmd.encode())
		exit()
	elif cmd == "Download_tempID":
		# Send command, receive tempID and display
		comm = cmd+"   "
		sock.sendall(comm.encode())
		temp_id = sock.recv(150).decode()
		print("Temp ID: "+temp_id)
	elif cmd == "Upload_contact_log":
		# Send command
		sock.sendall(cmd.encode())
		# Try open contact log and send to server line by line
		try: 
			f = open("z5112961_contactlog.txt","r")
			lines = f.readlines()
			if lines == []:	
				print("Error: No contact log")
				sock.sendall("none".encode())		
			else:
				for line in lines:
					split = line.split()
					print(split[0]+", "+split[1]+" "+split[2]+", "+split[3]+" "+split[4]+";")
					sock.sendall(line.encode())
				sock.sendall("break".encode())
		# Except send info saying no log and print error msg
		except:
			print("Error: No contact log")
			sock.sendall("none".encode())
	elif cmd[0:6] == "Beacon":
		# Call beacon function to handle
		peripheral(cmd)
	else:
		print("Error: Invalid command")
	
sock.close()
