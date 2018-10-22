# ICS 226 Lab 3
# Andrew Bishop
# Oct 19, 2018

import sys
import socket
import os

# declare variables
port = int(sys.argv[1])
if len(sys.argv) > 2:
    verbose = True if sys.argv[2] == '-v' else False
else:
    verbose = False

# declare functions
def recvWriteFile(filename, conn, size):
    with open(filename, "wb") as f:
        dataRemaining = size
        while dataRemaining > 0:
            data = conn.recv(min(1024, dataRemaining))
            if (dataRemaining == len(data)):
                f.write(data)
                conn.send("DONE".encode())
                dataRemaining = 0
            else:
                f.write(data)
                dataRemaining -= len(data)

def readSendFile(filename, conn, size):
    with open(filename, "rb") as f:
        dataRemaining = size
        while dataRemaining > 0:
            data = f.read(min(1024, dataRemaining))
            dataRemaining -= len(data)
            if (dataRemaining == 0):
                conn.send(data)
                conn.send("DONE".encode())
                break
            else:
                conn.send(data)

# open socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind socket to host and port
s.bind(('', port))
# listen
s.listen(0) # <-- how many concurrent clients can be 
            # queued, waiting for handshake

if verbose:
    print('server waiting on port %s' % port)

while True:

    # accept and send READY message
    conn, addr = s.accept() # creates a new socket, connected to client
    if verbose:
        print('server connected to client at ' + addr[0] + ':' + str(addr[1]))
    conn.send('READY'.encode())

    data = conn.recv(1024).decode()
    data = data.split(' ')
    request = data[0]
    filename = data[1]
    filepath = './' + filename

    ### ---- handle GET requests ----- ###
    if request == 'GET':
        if verbose:
            print('server receiving request: ' + request)
        # check if file requested is on server
        if os.path.isfile(filepath) == True:
            conn.send('OK'.encode())
            response = conn.recv(1024).decode()
            if response == 'READY':
                size = os.path.getsize(filename)
                size_bytes = size.to_bytes(8, byteorder='big', signed=False)
                conn.send(size_bytes)
                response = conn.recv(1024).decode()
                if response == 'OK':
                    if verbose:
                        print('server sending %d bytes' % size)
                    readSendFile(filename, conn, size)
        else:
            msg = 'ERROR: file %s does not exist' % filename
            conn.send(msg.encode())
        #send OK
            
    ### --- Handle PUT Requests --- ###
    elif request == 'PUT':
        if verbose:
            print('server receiving request: ' + request)
        conn.send('OK'.encode())
        # check if OS can create file (permissions, etc)
        # receive number of bytes
        size = int.from_bytes(conn.recv(8), byteorder='big', signed=False)
        if verbose:
            print('server receiving %d bytes' % size)
        conn.send('OK'.encode())
        # receive bytes in 1024 blocks
        recvWriteFile(filename, conn, size)
        

    ### --- Handle DEL Requests --- ###
    elif request == 'DEL':
        if verbose:
            print('server receiving request: ' + request)
        # check permissions
        try:
            print('server deleting file %s' % filename)
            os.remove(filename)
            conn.send('DONE'.encode())
        except:
            msg = 'ERROR: unable to delete %s' % filename
            conn.send(msg.encode())

            
