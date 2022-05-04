from socket import *
import threading
from sys import *
from datetime import datetime,timedelta
from random import randint
import time

blocked_users = []
contact_list = []
lock = threading.Condition()

#check arguments
if len(argv) != 3:
	print("Usage: server.py server_port block_duration")
	exit()
server_port = int(argv[1])
block_duration = float(argv[2])

def temp_id_generate(connection,uname):
	global lock

	# generate new 20 digit number
	for i in range(20):
		n = str(randint(0,9))
		if i == 0:
			new_tempid = n
		else:
			new_tempid = new_tempid+n
	# collect date info (now and 15 mins later)
	now = datetime.now()
	start = now.strftime("%d/%m/%Y %H:%M:%S")
	later = now+timedelta(minutes=15)
	end = later.strftime("%d/%m/%Y %H:%M:%S")
	info = uname+" "+new_tempid+" "+start+" "+end
	# writeinfo to tempIDs.txt
	with lock:
		f = open("tempIDs.txt", "a+")
		f.write(info+"\n")
		f.close()
		# display temp id and send to client
		print("Temp ID: "+new_tempid)
		connection.sendall(new_tempid.encode())
		lock.notify()

def login_delay(connection,uname):
	global blocked_users
	global lock
	global block_duration
	
	# sleep for 60 sec and remove username from list
	time.sleep(block_duration)

	with lock:	
		blocked_users.remove(uname)
		lock.notify()

def login(connection):
	global blocked_users

	unsuccessful = 0
	while True:
		data = connection.recv(50).decode()
		if data == "":
			continue
		# Get credentials.txt and compare to credentials
		f = open("credentials.txt","r")
		lines = f.readlines()
		file_flag = 0
		if data in lines:
			file_flag = 1
		# check if user blocked
		block_flag = 0
		uname = data.split()[0]
		if uname in blocked_users:
			block_flag = 1
		# Send whether valid or invalid to client
		if (file_flag == 1) and (unsuccessful < 2) and (block_flag == 0):
			connection.sendall("Welcome to the BlueTrace Simulator!".encode())
			print("user: "+uname)
			while True:
				cmd = connection.recv(18).decode()
				print cmd
				if cmd == "Download_tempID   ":
					#set up write temp id to file thread
					temp_id_thread=threading.Thread(target=temp_id_generate, args=(connection,uname,))
					temp_id_thread.daemon=True
					temp_id_thread.start()
				elif cmd == "Upload_contact_log":
					print("Received contact log from: "+uname)
					contact_list = []
					while True:
						log = connection.recv(61).decode()
						if log == "break":
							break
						if log == "none":
							print("Error: No contact log")
							break
						split = log.split()
						print(split[0]+", "+split[1]+" "+split[2]+", "+split[3]+" "+split[4]+";")
						# split line get temp id and 
						tempid = log.split()[0]
						f = open("tempIDs.txt","r")
						tempIDs = f.readlines()
						# check each line and if is there get info
						for line in tempIDs:
							if tempid in line:
								split = line.split()
								l = split[0]+", "+split[2]+" "+split[3]+", "+split[1]+";"
								contact_list.append(l)
						f.close()
					if log != "none":
						print("Contact log checking")
					for c in contact_list:
						print c	
				else:
					print(uname+" logout")
					break
		elif (file_flag == 0) and (unsuccessful < 2) and (block_flag == 1):
			connection.sendall("Your account is blocked due to multiple login failures. Please try again later".encode())
		elif (file_flag == 0) and (unsuccessful < 2):
			unsuccessful = unsuccessful+1
			connection.sendall("Invalid Password. Please try again".encode())
		else:
			connection.sendall("Your account is blocked due to multiple login failures. Please try again later".encode())
			#write the username to list
			uname = data.split()[0]
			blocked_users.append(uname)
			#set up timer thread
			timer_thread=threading.Thread(target=login_delay, args=(connection,uname,))
			timer_thread.daemon=True
			timer_thread.start()
			break

# Create a TCP/IP socket
sock = socket(AF_INET, SOCK_STREAM)
sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
# Bind the socket to the port
server_address = ('localhost', server_port)
#print ('Starting up on %s port %s' % server_address)
sock.bind(server_address)
# Listen for incoming connections
sock.listen(1)

while True:
	connection, client_address = sock.accept()
	login_thread=threading.Thread(target=login, args=(connection,))
	login_thread.daemon=True
	login_thread.start()
