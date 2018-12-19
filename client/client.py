# ICS 226 Lab 3
# Andrew Bishop
# Oct 19, 2018

import sys
import socket
import os
import os.path

# declare variables
server = sys.argv[1]
port = int(sys.argv[2])
command = sys.argv[3]
filename = sys.argv[4]

# declare functions
def recvWriteFile(filename, s, size):
    with open(filename, "wb") as f:
        dataRemaining = size
        while dataRemaining > 0:
            data = s.recv(min(1024, dataRemaining))
            if (dataRemaining == len(data)):
                f.write(data)
                end = s.recv(1024).decode("utf-8")
                if end == "DONE":
                    print("Complete")
                    dataRemaining = 0
                    s.close()
            else:
                f.write(data)
                dataRemaining -= len(data)

def readSendFile(filename, s, size):
    with open(filename, "rb") as f:
        dataRemaining = size
        while dataRemaining > 0:
            data = f.read(min(1024, dataRemaining))
            dataRemaining -= len(data)
            if (dataRemaining == 0):
                s.send(data)
                end = s.recv(1024).decode("utf-8")
                if end == "DONE":
                    print("Complete")
                    dataRemaining = 0
                    s.close()
            else:
                s.send(data)

# create an INET, STREAMing socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
	s.connect( (server, port) )
except Exception as e:
	print('\nSomething has gone wrong with host %s. Exception is %s ' % (server, e))

# wait for READY from server
print("connected")
data = s.recv(1024).decode()
if data == 'READY':
    print("get here")
    ### ---- handle GET requests ----- ###
    if command == 'GET':
        try:
            request = '%s %s' % (command, filename) 
            s.send(request.encode())
            response = s.recv(1024).decode()
            if response == 'OK':
                s.send('READY'.encode())
                # receive file's number of bytes from server (8 byte, unsigned)
                byte = s.recv(8)
                size = int.from_bytes(byte, byteorder='big', signed=False)
                s.send('OK'.encode())
                print('client receiving file %s (%d bytes)' % (filename, size)) 
                recvWriteFile(filename, s, size)
            else:
                # trim the "error" portion and print it
                response = response[7:] 
                print('server error: %s' % response)
                s.close()
        except Exception as e:
            print('Something went wrong. Exception is %s' % e)

    ### --- Handle PUT Requests --- ###
    elif command == 'PUT':
        try:    
            request = '%s %s' % (command, filename)
            s.send(request.encode())
            # receive OK or error from server
            response = s.recv(1024).decode()
            if response == 'OK':
                #send number of bytes (8 byte, unsigned)
                size = os.path.getsize(filename)
                size_bytes = size.to_bytes(8, byteorder='big', signed=False)
                s.send(size_bytes)
                # receive OK from server
                response = s.recv(1024).decode()
                if response == 'OK':
                    print('client sending file %s (%d bytes)' % (filename, size))
                    readSendFile(filename, s, size)
            else:
                response = response[7:]
                print('server error: %s' % response)
                s.close()
        except Exception as e:
            print('Something went wrong. Exception is %s' % e)

    ### --- Handle DEL Requests --- ###
    elif command == 'DEL':
        request = '%s %s' % (command, filename) 
        s.send(request.encode())
        print('client deleting file %s' % filename)
        s.send(request.encode())
        # receive DONE or error from server
        response = s.recv(1024).decode()
        if response == 'DONE':
            print('Complete')
            s.close()
        else:
            response = response[7:]
            print('server error: %s' % response)
            s.close()

