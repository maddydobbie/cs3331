import sys
from socket import *

def main():
	# checking usage
	if len(sys.argv) != 2:
		print("Usage: python WebServer.py port")
		exit(1)
	# getting the port
	serverPort = int(sys.argv[1])
	# creating the socket and binding to port	
	serverSocket = socket(AF_INET, SOCK_STREAM)
	serverSocket.bind(('',serverPort))
	serverSocket.listen(1)
	#print("here we go bois")
	while(1):
		# estabilish connection
		print("Server ready...")
		connectionSocket, addr = serverSocket.accept()
		try:
			# Receive request
			message = connectionSocket.recv(1024)
			# Isolate filename
			filename = message.split()[1]
			print(filename)
			# Open file to get data
			f = open(filename[1:])
			outputdata = f.read()
			# Send data to socket
			connectionSocket.send('\nHTTP/1.1 200 OK\n\n')
			connectionSocket.send(outputdata)
			connectionSocket.close()
		except IOError:
			msg = 'HTTP/1.1 404 Not Found'
			connectionSocket.send(msg.encode())
			connectionSocket.close()
	pass

if __name__ == '__main__':
	main()
